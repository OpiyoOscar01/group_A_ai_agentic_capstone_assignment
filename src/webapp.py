"""Flask API and local web entry point for CampusIQ."""
import json
import os
import re
import secrets
import sqlite3
import sys
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory, session
from werkzeug.exceptions import HTTPException

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import agent as agent_module  # noqa: E402
import rag  # noqa: E402
import tools  # noqa: E402

try:
    from dotenv import load_dotenv

    load_dotenv(BASE / ".env")
except ImportError:
    pass


def connect_database(path):
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    return connection


def initialize_database(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect_database(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS handbook_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                query TEXT NOT NULL,
                decision TEXT NOT NULL,
                sources_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_handbook_searches_student_created "
            "ON handbook_searches(student_id, created_at DESC)"
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversations_student_updated "
            "ON conversations(student_id, updated_at DESC)"
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversation_messages_conversation "
            "ON conversation_messages(conversation_id, id)"
        )


def save_search(path, student_id, query, result):
    with connect_database(path) as connection:
        connection.execute(
            "INSERT INTO handbook_searches "
            "(student_id, query, decision, sources_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                student_id,
                query,
                result["decision"],
                json.dumps(result.get("sources", [])),
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def list_searches(path, student_id, limit=30):
    with connect_database(path) as connection:
        rows = connection.execute(
            "SELECT id, query, decision, sources_json, created_at "
            "FROM handbook_searches WHERE student_id = ? "
            "ORDER BY created_at DESC, id DESC LIMIT ?",
            (student_id, limit),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "query": row["query"],
            "decision": row["decision"],
            "sources": json.loads(row["sources_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def create_conversation(path, student_id):
    timestamp = datetime.now(timezone.utc).isoformat()
    with connect_database(path) as connection:
        cursor = connection.execute(
            "INSERT INTO conversations (student_id, title, created_at, updated_at) "
            "VALUES (?, ?, ?, ?)",
            (student_id, "New conversation", timestamp, timestamp),
        )
        return cursor.lastrowid


def conversation_belongs_to(path, conversation_id, student_id):
    with connect_database(path) as connection:
        return connection.execute(
            "SELECT 1 FROM conversations WHERE id = ? AND student_id = ?",
            (conversation_id, student_id),
        ).fetchone() is not None


def save_conversation_message(path, conversation_id, role, content, metadata=None):
    timestamp = datetime.now(timezone.utc).isoformat()
    with connect_database(path) as connection:
        connection.execute(
            "INSERT INTO conversation_messages "
            "(conversation_id, role, content, metadata_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (conversation_id, role, content, json.dumps(metadata or {}), timestamp),
        )
        if role == "user":
            title = " ".join(content.split())[:72] or "New conversation"
            connection.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title, timestamp, conversation_id),
            )
        else:
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (timestamp, conversation_id),
            )


def list_conversations(path, student_id):
    with connect_database(path) as connection:
        rows = connection.execute(
            """
            SELECT c.id, c.title, c.created_at, c.updated_at,
                   (SELECT m.content FROM conversation_messages m
                    WHERE m.conversation_id = c.id ORDER BY m.id DESC LIMIT 1) AS preview
            FROM conversations c
            WHERE c.student_id = ?
            ORDER BY c.updated_at DESC, c.id DESC
            """,
            (student_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_conversation_messages(path, conversation_id):
    with connect_database(path) as connection:
        rows = connection.execute(
            "SELECT id, role, content, metadata_json, created_at "
            "FROM conversation_messages WHERE conversation_id = ? ORDER BY id",
            (conversation_id,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "role": row["role"],
            "text": row["content"],
            "metadata": json.loads(row["metadata_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def create_app(database_path=None, planner_factory=None):
    app = Flask(__name__, static_folder=str(BASE / "frontend" / "dist"), static_url_path="")
    app.config.update(
        SECRET_KEY=os.environ.get("CAMUS_SECRET_KEY") or secrets.token_hex(32),
        DATABASE=str(database_path or os.environ.get(
            "CAMUS_DB_PATH", BASE / "data" / "camus_iq.sqlite3"
        )),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    app.config["PLANNER_FACTORY"] = planner_factory or agent_module.GeminiPlanner
    initialize_database(app.config["DATABASE"])
    active_sessions = {}
    app.extensions["camus_sessions"] = active_sessions

    def current_student():
        student_id = session.get("student_id")
        if not student_id or not tools.STUDENT_ID_RE.fullmatch(str(student_id)):
            return None
        student = next(
            (item for item in tools._load("students.json") or []
             if item.get("student_id") == student_id),
            None,
        )
        if not student:
            session.clear()
            return None
        session_key = session.get("camus_session_key")
        if not session_key:
            session.clear()
            return None
        if session_key not in active_sessions:
            active_sessions[session_key] = {}
        return student, active_sessions[session_key]

    def request_payload():
        body = request.get_json(silent=True)
        return body if isinstance(body, dict) else {}

    def authenticated(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_student()
            if user is None:
                return jsonify({"error": "Please sign in with a demo student ID to continue."}), 401
            g.student, g.agent_sessions = user[0], user[1]
            return view(*args, **kwargs)
        return wrapped

    def documents():
        result = []
        for file_path in sorted(rag.KNOW.glob("*.txt")):
            with file_path.open(encoding="utf-8") as source:
                first_line = source.readline().strip()
            match = re.search(r"DOC-ID:\s*(DOC-\d+)\s*\|\s*Title:\s*([^|]+)", first_line)
            if match:
                result.append({
                    "id": match.group(1),
                    "title": match.group(2).strip(),
                    "file": file_path.name,
                })
        return result

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        if isinstance(error, HTTPException):
            return error
        app.logger.exception("CampusIQ request failed")
        return jsonify({"error": "CampusIQ could not complete that request. Please try again."}), 500

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "CampusIQ",
            "model_provider": "Gemini",
            "model": os.environ.get("GEMINI_MODEL", "gemini-3.8-flash"),
            "model_configured": bool(os.environ.get("GEMINI_API_KEY", "").strip()),
        })

    @app.get("/api/demo-students")
    def demo_students():
        students = tools._load("students.json") or []
        return jsonify([
            {"student_id": item["student_id"], "name": item["name"]}
            for item in students
        ])

    @app.post("/api/session")
    def sign_in():
        body = request_payload()
        student_id = str(body.get("student_id", "")).strip()
        if not tools.STUDENT_ID_RE.fullmatch(student_id):
            return jsonify({"error": "Enter a valid 10-digit demo student ID."}), 400
        student = next(
            (item for item in tools._load("students.json") or []
             if item.get("student_id") == student_id),
            None,
        )
        if not student:
            return jsonify({"error": "That ID is not in the synthetic demo roster."}), 403
        session.clear()
        session["student_id"] = student_id
        session["camus_session_key"] = secrets.token_urlsafe(24)
        active_sessions[session["camus_session_key"]] = {}
        return jsonify({
            "student": {"student_id": student_id, "name": student["name"]},
            "model_provider": "Gemini",
            "model_configured": bool(os.environ.get("GEMINI_API_KEY", "").strip()),
        })

    @app.get("/api/session")
    def get_session():
        user = current_student()
        if user is None:
            return jsonify({"authenticated": False})
        student, agent_sessions = user
        active_conversation_id = session.get("active_conversation_id")
        active_entry = agent_sessions.get(active_conversation_id)
        agent_session = active_entry[1] if active_entry else None
        current_run = agent_session.run if agent_session else None
        return jsonify({
            "authenticated": True,
            "student": {"student_id": student["student_id"], "name": student["name"]},
            "active_conversation_id": active_conversation_id,
            "model_provider": "Gemini",
            "model_configured": bool(os.environ.get("GEMINI_API_KEY", "").strip()),
            "run_status": current_run.status if current_run else None,
            "awaiting_approval": bool(current_run and current_run.status == "awaiting_approval"),
            "pending_draft": (
                current_run.approval["draft"]
                if current_run and current_run.status == "awaiting_approval"
                else None
            ),
        })

    @app.post("/api/logout")
    @authenticated
    def sign_out():
        session_key = session.get("camus_session_key")
        active_sessions.pop(session_key, None)
        session.clear()
        return jsonify({"ok": True})

    @app.get("/api/overview")
    @authenticated
    def overview():
        student_id = g.student["student_id"]
        cases_result = tools.lookup_case_or_timetable(student_id, "my_cases")
        timetable_result = tools.lookup_case_or_timetable(student_id, "timetable")
        if cases_result.get("status") != "ok":
            return jsonify({"error": "Your case service is unavailable right now."}), 503
        if timetable_result.get("error_code") == "SERVICE_UNAVAILABLE":
            return jsonify({"error": "The timetable service is unavailable right now."}), 503
        cases = cases_result.get("data", {}).get("cases", []) if cases_result.get("status") == "ok" else []
        timetable = timetable_result.get("data") if timetable_result.get("status") == "ok" else None
        open_cases = [case for case in cases if case.get("status") in agent_module.OPEN_STATUSES]
        recent_searches = list_searches(app.config["DATABASE"], student_id, limit=4)
        return jsonify({
            "student": {"student_id": student_id, "name": g.student["name"]},
            "case_count": len(cases),
            "open_case_count": len(open_cases),
            "search_count": len_searches(app.config["DATABASE"], student_id),
            "recent_cases": cases[:4],
            "timetable": timetable,
            "recent_searches": recent_searches,
        })

    @app.get("/api/conversations")
    @authenticated
    def conversations():
        return jsonify({
            "conversations": list_conversations(
                app.config["DATABASE"], g.student["student_id"]
            )
        })

    @app.post("/api/conversations")
    @authenticated
    def new_conversation():
        conversation_id = create_conversation(
            app.config["DATABASE"], g.student["student_id"]
        )
        session["active_conversation_id"] = conversation_id
        return jsonify({"conversation_id": conversation_id}), 201

    def conversation_transcript(conversation_id):
        student_id = g.student["student_id"]
        if not conversation_belongs_to(app.config["DATABASE"], conversation_id, student_id):
            return jsonify({"error": "Conversation not found."}), 404
        rows = list_conversation_messages(app.config["DATABASE"], conversation_id)
        active_entry = g.agent_sessions.get(conversation_id)
        current_run = active_entry[1].run if active_entry else None
        pending_draft = (
            current_run.approval.get("draft")
            if current_run and current_run.status == "awaiting_approval"
            else None
        )
        for row in rows:
            if row["role"] == "assistant":
                row["can_approve"] = bool(
                    pending_draft and row["metadata"].get("draft") == pending_draft
                )
        return jsonify({"conversation_id": conversation_id, "messages": rows})

    @app.get("/api/conversations/<int:conversation_id>/messages")
    @authenticated
    def conversation_messages(conversation_id):
        return conversation_transcript(conversation_id)

    @app.post("/api/conversations/<int:conversation_id>/open")
    @authenticated
    def open_conversation(conversation_id):
        if not conversation_belongs_to(
            app.config["DATABASE"], conversation_id, g.student["student_id"]
        ):
            return jsonify({"error": "Conversation not found."}), 404
        session["active_conversation_id"] = conversation_id
        return conversation_transcript(conversation_id)

    @app.delete("/api/conversations/<int:conversation_id>")
    @authenticated
    def delete_conversation(conversation_id):
        with connect_database(app.config["DATABASE"]) as connection:
            cursor = connection.execute(
                "DELETE FROM conversations WHERE id = ? AND student_id = ?",
                (conversation_id, g.student["student_id"]),
            )
        if cursor.rowcount == 0:
            return jsonify({"error": "Conversation not found."}), 404
        g.agent_sessions.pop(conversation_id, None)
        if session.get("active_conversation_id") == conversation_id:
            session.pop("active_conversation_id", None)
        return jsonify({"ok": True})

    @app.delete("/api/conversations")
    @authenticated
    def clear_conversations():
        with connect_database(app.config["DATABASE"]) as connection:
            connection.execute(
                "DELETE FROM conversations WHERE student_id = ?",
                (g.student["student_id"],),
            )
        g.agent_sessions.clear()
        session.pop("active_conversation_id", None)
        return jsonify({"ok": True})

    @app.get("/api/cases")
    @authenticated
    def cases():
        result = tools.lookup_case_or_timetable(g.student["student_id"], "my_cases")
        if result.get("status") != "ok":
            return jsonify({"error": "Your case service is unavailable right now."}), 503
        return jsonify({"cases": result["data"]["cases"]})

    @app.get("/api/timetable")
    @authenticated
    def timetable():
        result = tools.lookup_case_or_timetable(g.student["student_id"], "timetable")
        if result.get("status") != "ok":
            return jsonify({"timetable": None, "message": "No timetable is available for this demo student."})
        return jsonify({"timetable": result["data"]})

    @app.get("/api/handbook/documents")
    @authenticated
    def handbook_documents():
        return jsonify({"documents": documents()})

    @app.post("/api/handbook/search")
    @authenticated
    def handbook_search():
        body = request_payload()
        query = body.get("query")
        if not isinstance(query, str) or not query.strip():
            return jsonify({"error": "Enter a handbook question to search."}), 400
        query = query.strip()
        if len(query) > 300:
            return jsonify({"error": "Keep handbook searches under 300 characters."}), 400
        answer = rag.answer(query)
        hits = rag.retrieve(query)
        document_titles = {item["id"]: item["title"] for item in documents()}
        result = {
            "query": query,
            "decision": answer["decision"],
            "answer": answer["answer"],
            "sources": answer.get("sources", []),
            "results": [
                {
                    "doc_id": item["doc_id"],
                    "title": document_titles.get(item["doc_id"], item["file"]),
                    "excerpt": item["text"][:360],
                    "score": item["score"],
                }
                for item in hits
                if item["score"] >= rag.MIN_SCORE
            ],
        }
        save_search(app.config["DATABASE"], g.student["student_id"], query, result)
        return jsonify(result)

    @app.get("/api/search-history")
    @authenticated
    def search_history():
        return jsonify({"searches": list_searches(app.config["DATABASE"], g.student["student_id"])})

    @app.delete("/api/search-history")
    @authenticated
    def clear_search_history():
        with connect_database(app.config["DATABASE"]) as connection:
            connection.execute(
                "DELETE FROM handbook_searches WHERE student_id = ?",
                (g.student["student_id"],),
            )
        return jsonify({"ok": True})

    @app.post("/api/chat")
    @authenticated
    def chat():
        body = request_payload()
        message = body.get("message")
        if not isinstance(message, str) or not message.strip():
            return jsonify({"error": "Type a message before sending."}), 400
        if len(message) > agent_module.MAX_INPUT_CHARS:
            return jsonify({"error": "Messages must be 1,000 characters or fewer."}), 400
        conversation_id = body.get("conversation_id")
        if conversation_id is None:
            conversation_id = create_conversation(
                app.config["DATABASE"], g.student["student_id"]
            )
        elif (
            isinstance(conversation_id, bool)
            or not isinstance(conversation_id, int)
            or conversation_id < 1
        ):
            return jsonify({"error": "Invalid conversation ID."}), 400
        elif not conversation_belongs_to(
            app.config["DATABASE"], conversation_id, g.student["student_id"]
        ):
            return jsonify({"error": "Conversation not found."}), 404

        active_entry = g.agent_sessions.get(conversation_id)
        if active_entry is None:
            agent_session = agent_module.Session(
                g.student["student_id"], name=g.student["name"]
            )
            agent = agent_module.Agent(app.config["PLANNER_FACTORY"]())
            g.agent_sessions[conversation_id] = (agent, agent_session)
        else:
            agent, agent_session = active_entry
        session["active_conversation_id"] = conversation_id
        save_conversation_message(
            app.config["DATABASE"], conversation_id, "user", message
        )
        result = agent.handle_turn(agent_session, message)
        current_run = agent_session.run
        pending_draft = (
            current_run.approval["draft"]
            if current_run and current_run.status == "awaiting_approval"
            else None
        )
        save_conversation_message(
            app.config["DATABASE"],
            conversation_id,
            "assistant",
            result["message"],
            {"draft": pending_draft} if pending_draft else {},
        )
        return jsonify({
            "conversation_id": conversation_id,
            "message": result["message"],
            "final": result.get("final", True),
            "route": result.get("route"),
            "stop_reason": result.get("stop_reason"),
            "run_status": current_run.status if current_run else None,
            "awaiting_approval": bool(pending_draft),
            "pending_draft": pending_draft,
        })

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def frontend(path):
        build_dir = BASE / "frontend" / "dist"
        if not build_dir.is_dir():
            return (
                "CampusIQ frontend is not built. Start the frontend with `npm run dev` "
                "from the frontend folder, or run `npm run build` for production.",
                503,
            )
        requested = build_dir / path
        if path and requested.is_file():
            return send_from_directory(build_dir, path)
        return send_from_directory(build_dir, "index.html")

    return app


def len_searches(path, student_id):
    with connect_database(path) as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM handbook_searches WHERE student_id = ?",
            (student_id,),
        ).fetchone()[0]


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
