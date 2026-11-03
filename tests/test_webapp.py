import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import webapp


BASE = Path(__file__).resolve().parents[1]


class CamusWebTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="camus_web_")
        self.root = Path(self.temporary.name)
        shutil.copytree(BASE / "data", self.root / "data")
        self.original_data = webapp.tools.DATA
        webapp.tools.DATA = str(self.root / "data")
        self.app = webapp.create_app(
            self.root / "camus.sqlite3",
            planner_factory=webapp.agent_module.ScriptedPlanner,
        )
        self.app.config.update(TESTING=True, SECRET_KEY="test-session-secret")
        self.client = self.app.test_client()

    def tearDown(self):
        webapp.tools.DATA = self.original_data
        self.temporary.cleanup()

    def sign_in(self, student_id="2300701098"):
        return self.client.post("/api/session", json={"student_id": student_id})

    def test_demo_sign_in_requires_a_registered_sample_student(self):
        self.assertEqual(self.sign_in("123").status_code, 400)
        self.assertEqual(self.sign_in("9999999999").status_code, 403)
        self.assertEqual(self.client.get("/api/cases").status_code, 401)
        self.assertEqual(self.sign_in().status_code, 200)

    def test_handbook_search_persists_metadata_and_scopes_history_to_student(self):
        self.assertEqual(self.sign_in().status_code, 200)
        response = self.client.post(
            "/api/handbook/search",
            json={"query": "How many times can I retake a failed course?"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("DOC-01", response.json["sources"])

        history = self.client.get("/api/search-history").json["searches"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["query"], "How many times can I retake a failed course?")
        self.assertEqual(history[0]["decision"], "grounded")
        self.assertNotIn("answer", history[0])

        restarted_app = webapp.create_app(self.root / "camus.sqlite3")
        restarted_app.config["PLANNER_FACTORY"] = webapp.agent_module.ScriptedPlanner
        restarted_app.config.update(TESTING=True, SECRET_KEY="test-session-secret")
        restarted_client = restarted_app.test_client()
        self.assertEqual(
            restarted_client.post(
                "/api/session", json={"student_id": "2300701098"}
            ).status_code,
            200,
        )
        persisted_history = restarted_client.get("/api/search-history").json["searches"]
        self.assertEqual(len(persisted_history), 1)

        second_client = self.app.test_client()
        self.assertEqual(
            second_client.post("/api/session", json={"student_id": "2300700445"}).status_code,
            200,
        )
        self.assertEqual(second_client.get("/api/search-history").json["searches"], [])

    def test_case_creation_requires_explicit_approval(self):
        self.assertEqual(self.sign_in("2300716574").status_code, 200)
        before = self.client.get("/api/cases").json["cases"]

        draft = self.client.post(
            "/api/chat",
            json={"message": "I need to retake BIT9999, semester 2026-S1"},
        )
        self.assertEqual(draft.status_code, 200, draft.get_json())
        self.assertTrue(draft.json["awaiting_approval"])
        self.assertEqual(draft.json["pending_draft"]["category"], "retake")
        self.assertEqual(self.client.get("/api/cases").json["cases"], before)
        conversation_id = draft.json["conversation_id"]
        pending_message = self.client.get(
            f"/api/conversations/{conversation_id}/messages"
        ).json["messages"][-1]
        self.assertTrue(pending_message["can_approve"])

        restarted_app = webapp.create_app(
            self.root / "camus.sqlite3",
            planner_factory=webapp.agent_module.ScriptedPlanner,
        )
        restarted_app.config.update(TESTING=True, SECRET_KEY="test-session-secret")
        restarted_client = restarted_app.test_client()
        restarted_client.post(
            "/api/session", json={"student_id": "2300716574"}
        )
        reopened = restarted_client.post(
            f"/api/conversations/{conversation_id}/open"
        ).json["messages"][-1]
        self.assertFalse(reopened["can_approve"])

        approved = self.client.post(
            "/api/chat",
            json={
                "message": "yes",
                "conversation_id": conversation_id,
            },
        )
        self.assertEqual(approved.status_code, 200, approved.get_json())
        self.assertEqual(approved.json["stop_reason"], "GOAL_MET")
        after = self.client.get("/api/cases").json["cases"]
        self.assertEqual(len(after), len(before) + 1)
        self.assertEqual(after[-1]["status"], "Pending")

    def test_existing_timetable_and_document_collection_are_available(self):
        self.assertEqual(self.sign_in().status_code, 200)
        timetable = self.client.get("/api/timetable").json["timetable"]
        self.assertEqual(timetable["semester"], "2026-S1")
        self.assertTrue(timetable["entries"])
        documents = self.client.get("/api/handbook/documents").json["documents"]
        self.assertEqual(len(documents), 12)
        self.assertEqual(documents[0]["id"], "DOC-01")

    def test_search_history_can_be_cleared(self):
        self.assertEqual(self.sign_in().status_code, 200)
        self.client.post("/api/handbook/search", json={"query": "retake failed course"})
        cleared = self.client.delete("/api/search-history")
        self.assertEqual(cleared.status_code, 200)
        self.assertEqual(self.client.get("/api/search-history").json["searches"], [])

    def test_chat_transcripts_persist_and_are_scoped_to_the_demo_student(self):
        self.assertEqual(self.sign_in().status_code, 200)
        reply = self.client.post(
            "/api/chat",
            json={"message": "How many times can I retake a failed course?"},
        )
        self.assertEqual(reply.status_code, 200, reply.get_json())
        conversation_id = reply.json["conversation_id"]
        self.assertIn("[Source:", reply.json["message"])

        transcript = self.client.get(
            f"/api/conversations/{conversation_id}/messages"
        ).json["messages"]
        self.assertEqual([item["role"] for item in transcript], ["user", "assistant"])

        restarted_app = webapp.create_app(
            self.root / "camus.sqlite3",
            planner_factory=webapp.agent_module.ScriptedPlanner,
        )
        restarted_app.config.update(TESTING=True, SECRET_KEY="test-session-secret")
        restarted_client = restarted_app.test_client()
        self.assertEqual(
            restarted_client.post(
                "/api/session", json={"student_id": "2300701098"}
            ).status_code,
            200,
        )
        saved = restarted_client.get("/api/conversations").json["conversations"]
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]["id"], conversation_id)
        self.assertEqual(
            len(
                restarted_client.get(
                    f"/api/conversations/{conversation_id}/messages"
                ).json["messages"]
            ),
            2,
        )

        other_student = self.app.test_client()
        self.assertEqual(
            other_student.post(
                "/api/session", json={"student_id": "2300700445"}
            ).status_code,
            200,
        )
        self.assertEqual(other_student.get("/api/conversations").json["conversations"], [])
        self.assertEqual(
            other_student.get(
                f"/api/conversations/{conversation_id}/messages"
            ).status_code,
            404,
        )
        self.assertEqual(
            other_student.delete(f"/api/conversations/{conversation_id}").status_code,
            404,
        )
        self.assertEqual(
            restarted_client.post(f"/api/conversations/{conversation_id}/open").status_code,
            200,
        )
        self.assertEqual(
            restarted_client.get("/api/session").json["active_conversation_id"],
            conversation_id,
        )
        self.assertEqual(
            restarted_client.delete(f"/api/conversations/{conversation_id}").status_code,
            200,
        )
        self.assertEqual(restarted_client.get("/api/conversations").json["conversations"], [])

    def test_student_can_delete_all_saved_conversations(self):
        self.assertEqual(self.sign_in().status_code, 200)
        first = self.client.post("/api/conversations")
        second = self.client.post("/api/conversations")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(len(self.client.get("/api/conversations").json["conversations"]), 2)

        self.assertEqual(self.client.delete("/api/conversations").status_code, 200)
        self.assertEqual(self.client.get("/api/conversations").json["conversations"], [])

    def test_web_app_defaults_to_gemini_planner(self):
        app = webapp.create_app(self.root / "gemini.sqlite3")
        self.assertIs(app.config["PLANNER_FACTORY"], webapp.agent_module.GeminiPlanner)

    def test_gemini_planner_requires_a_configured_key(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"):
                webapp.agent_module.GeminiPlanner().propose({})


if __name__ == "__main__":
    unittest.main()
