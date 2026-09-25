"""Week 4 Tool/Function-Calling layer – University Student-Support Case Agent.
Group A Day | BSE4104 | Implements Lily's Tool Catalogue (4 tools).

Tools:
  1. get_timetable(student_id, semester?) – live timetable store lookup
  2. get_case_status(case_id, student_id) – live case store lookup (ownership-checked)
  3. search_knowledge_base(query, top_k=3, min_score=0.14) – TF-IDF corpus retrieval
  4. create_support_case(student_id, category, subject, description) – draft-only side effect,
     status always server-assigned "Pending", created_by "agent_draft".

Design (orchestrator is authority):
- Every tool validates its arguments against its JSON schema BEFORE executing.
- Authorization checks run in deterministic code, never in the model.
- All returns are structured dicts; failures return {"error": ...} envelopes,
  never fabricated records.
- Deliberately NO approve/resolve/grade/admit/fee/delete tools exist.

Run:
  python src/tools.py --demo
  python src/tools.py --call get_timetable --args '{"student_id":"2300701330"}'
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
TIMETABLE_FILE = BASE / "data" / "timetable.json"
CASES_FILE = BASE / "data" / "cases.json"
CURRENT_SEMESTER = "2026-S1"

VALID_CATEGORIES = ["missing_marks", "retake_request", "registration_issue", "timetable_clash"]

# ---------------------------------------------------------------- schemas ---
TOOL_SCHEMAS = {
    "get_timetable": {
        "name": "get_timetable",
        "description": "Retrieve the authenticated student's timetable for a given semester.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "pattern": "^[0-9]{10}$",
                               "description": "Must equal the authenticated session's student ID."},
                "semester": {"type": "string", "pattern": "^[0-9]{4}-S[12]$",
                             "description": "Defaults to the current semester if omitted."},
            },
            "required": ["student_id"],
            "additionalProperties": False,
        },
    },
    "get_case_status": {
        "name": "get_case_status",
        "description": "Retrieve the status of a support case belonging to the authenticated student.",
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {"type": "string", "pattern": "^CASE-[0-9]{4}$"},
                "student_id": {"type": "string", "pattern": "^[0-9]{10}$",
                               "description": "Must equal the authenticated session's student ID."},
            },
            "required": ["case_id", "student_id"],
            "additionalProperties": False,
        },
    },
    "search_knowledge_base": {
        "name": "search_knowledge_base",
        "description": "Retrieve relevant excerpts from the approved knowledge corpus for grounded Q&A.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 3, "maxLength": 300},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 5, "default": 3},
                "min_score": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.14},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    "create_support_case": {
        "name": "create_support_case",
        "description": "Create a draft support case for the authenticated student. Status is always "
                       "server-assigned and cannot be set by the caller.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "pattern": "^[0-9]{10}$",
                               "description": "Must equal the authenticated session's student ID."},
                "category": {"type": "string",
                             "enum": ["missing_marks", "retake_request",
                                      "registration_issue", "timetable_clash"]},
                "subject": {"type": "string", "maxLength": 100},
                "description": {"type": "string", "maxLength": 500},
            },
            "required": ["student_id", "category", "subject", "description"],
            "additionalProperties": False,
        },
    },
}

FORBIDDEN_ARG_KEYS = {"status", "assigned_office", "assignee", "resolution",
                      "grade", "marks", "admission", "fee_waiver"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _err(code: str, message: str, **extra) -> dict:
    out = {"error": code, "message": message}
    out.update(extra)
    return out


# ------------------------------------------------------- validation helpers ---
def _check_no_forbidden_args(args: dict) -> str | None:
    found = FORBIDDEN_ARG_KEYS & set(args.keys())
    if found:
        return f"Forbidden argument(s): {sorted(found)}. Status and privileged fields cannot be set by the caller."
    return None


def validate_args(tool_name: str, args: dict) -> str | None:
    """Return None if valid, else an error message. Schema-level checks only."""
    schema = TOOL_SCHEMAS.get(tool_name)
    if schema is None:
        return f"Unknown tool: {tool_name}"
    if not isinstance(args, dict):
        return "Arguments must be a JSON object."
    params = schema["parameters"]
    # additionalProperties
    if not params.get("additionalProperties", True):
        allowed = set(params["properties"].keys())
        extra = set(args.keys()) - allowed
        if extra:
            return f"Unexpected argument(s): {sorted(extra)}. Allowed: {sorted(allowed)}."
    # forbidden privileged keys (defence in depth even if schema allowed them)
    bad = _check_no_forbidden_args(args)
    if bad:
        return bad
    # required
    for req in params.get("required", []):
        if req not in args or args[req] in (None, ""):
            return f"Missing required argument: {req}."
    props = params["properties"]
    # per-field checks
    if "student_id" in args and "student_id" in props:
        if not re.fullmatch(r"^[0-9]{10}$", str(args["student_id"])):
            return "Invalid student_id: must be 10 digits."
    if "case_id" in args and "case_id" in props:
        if not re.fullmatch(r"^CASE-[0-9]{4}$", str(args["case_id"]).upper()):
            return "Invalid case_id: expected format CASE-XXXX."
    if "semester" in args and args.get("semester") is not None:
        if not re.fullmatch(r"^[0-9]{4}-S[12]$", str(args["semester"])):
            return "Invalid semester: expected format YYYY-S1 or YYYY-S2."
    if "category" in args and "category" in props:
        if args["category"] not in VALID_CATEGORIES:
            return f"Invalid category: must be one of {VALID_CATEGORIES}."
    if "subject" in args and "subject" in props:
        if len(str(args["subject"])) > 100:
            return "Invalid subject: maximum 100 characters."
        if not str(args["subject"]).strip():
            return "Invalid subject: must not be empty."
    if "description" in args and "description" in props:
        if len(str(args["description"])) > 500:
            return "Invalid description: maximum 500 characters."
        if not str(args["description"]).strip():
            return "Invalid description: must not be empty."
    if "query" in args and "query" in props:
        q = str(args["query"])
        if not (3 <= len(q) <= 300):
            return "Invalid query: must be 3-300 characters."
    if "top_k" in args and args.get("top_k") is not None:
        try:
            k = int(args["top_k"])
        except (ValueError, TypeError):
            return "Invalid top_k: must be an integer 1-5."
        if not (1 <= k <= 5):
            return "Invalid top_k: must be an integer 1-5."
    if "min_score" in args and args.get("min_score") is not None:
        try:
            s = float(args["min_score"])
        except (ValueError, TypeError):
            return "Invalid min_score: must be a number 0-1."
        if not (0 <= s <= 1):
            return "Invalid min_score: must be a number 0-1."
    return None


# ------------------------------------------------------------------ tools ---
def get_timetable(args: dict, session: dict) -> dict:
    """Read-only lookup against the live timetable store."""
    problem = validate_args("get_timetable", args)
    if problem:
        return _err("invalid_arguments", problem, tool="get_timetable")
    sid = str(args["student_id"])
    if sid != str(session.get("student_id", "")):
        return _err("unauthorized",
                    "student_id does not match the authenticated session.",
                    tool="get_timetable")
    semester = args.get("semester") or CURRENT_SEMESTER
    try:
        store = json.loads(TIMETABLE_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _err("service_unavailable",
                    "Timetable store is unavailable. Please try again later.",
                    tool="get_timetable")
    except json.JSONDecodeError:
        return _err("service_unavailable",
                    "Timetable store is malformed. Staff have been notified.",
                    tool="get_timetable")
    record = store.get(sid)
    if record is None:
        return _err("not_found",
                    "I can't find a timetable for that student ID.",
                    tool="get_timetable", student_id=sid)
    classes = record.get("classes", [])
    entries = [{"course_code": c.get("code", ""), "day": c.get("day", ""),
                "time": c.get("time", ""), "room": c.get("venue", c.get("room", ""))}
               for c in classes] if semester == CURRENT_SEMESTER else []
    return {"student_id": sid, "semester": semester, "entries": entries,
            "retrieved_at": _now_iso()}


def get_case_status(args: dict, session: dict) -> dict:
    """Read-only lookup against the live case store (ownership-checked)."""
    problem = validate_args("get_case_status", args)
    if problem:
        return _err("invalid_arguments", problem, tool="get_case_status")
    sid = str(args["student_id"])
    cid = str(args["case_id"]).upper()
    if sid != str(session.get("student_id", "")):
        return _err("unauthorized",
                    "student_id does not match the authenticated session.",
                    tool="get_case_status")
    try:
        store = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _err("service_unavailable",
                    "Case store is unavailable. Please try again later.",
                    tool="get_case_status")
    except json.JSONDecodeError:
        return _err("service_unavailable",
                    "Case store is malformed. Staff have been notified.",
                    tool="get_case_status")
    record = store.get(cid)
    # Identical wording for not-found vs wrong-owner: do not leak existence.
    if record is None or str(record.get("student_id", "")) != sid:
        return _err("not_found",
                    "I can't find that case for your student ID. Please confirm your case ID.",
                    tool="get_case_status", case_id=cid)
    return {"case_id": cid, "status": record.get("status", "Pending"),
            "category": record.get("category", ""),
            "subject": record.get("summary", record.get("subject", "")),
            "created_at": record.get("created", ""),
            "updated_at": record.get("updated_at", record.get("created", ""))}


def search_knowledge_base(args: dict, session: dict) -> dict:
    """Read-only retrieval against the static DOC-01..DOC-12 corpus."""
    problem = validate_args("search_knowledge_base", args)
    if problem:
        return _err("invalid_arguments", problem, tool="search_knowledge_base")
    if not session.get("student_id"):
        return _err("unauthorized", "An authenticated session is required.",
                    tool="search_knowledge_base")
    query = str(args["query"])
    top_k = int(args.get("top_k", 3))
    min_score = float(args.get("min_score", 0.14))
    try:
        sys.path.insert(0, str(BASE / "src"))
        from rag import retrieve as rag_retrieve
        hits = rag_retrieve(query, k=top_k)
    except Exception as exc:
        return _err("service_unavailable",
                    f"Retrieval service failed: {exc}. Please try again later.",
                    tool="search_knowledge_base")
    results = [{"doc_id": h.get("doc_id", ""), "score": h.get("score", 0.0),
                "excerpt": h.get("text", "")[:220],
                "source_file": h.get("file", "")}
               for h in hits if h.get("score", 0) >= min_score][:top_k]
    return {"query": query, "results": results, "retrieved_at": _now_iso()}


def _next_case_id(store: dict) -> str:
    nums = [int(re.search(r"(\d+)", k).group(1)) for k in store.keys()
            if re.fullmatch(r"CASE-\d{4}", k)]
    nxt = (max(nums) + 1) if nums else 1001
    return f"CASE-{nxt:04d}"


def create_support_case(args: dict, session: dict) -> dict:
    """Low-risk simulated side effect: draft-only record, status locked Pending."""
    problem = validate_args("create_support_case", args)
    if problem:
        return _err("invalid_arguments", problem, tool="create_support_case")
    sid = str(args["student_id"])
    if sid != str(session.get("student_id", "")):
        return _err("unauthorized",
                    "student_id does not match the authenticated session.",
                    tool="create_support_case")
    try:
        store = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        store = {}
    except json.JSONDecodeError:
        return _err("service_unavailable",
                    "Case store is malformed. Staff have been notified.",
                    tool="create_support_case")
    cid = _next_case_id(store)
    record = {"student_id": sid, "category": args["category"],
              "summary": str(args["subject"]) + " — " + str(args["description"]),
              "subject": str(args["subject"]),
              "description": str(args["description"]),
              "status": "Pending", "created_by": "agent_draft",
              "created": _now_iso()}
    store[cid] = record
    try:
        CASES_FILE.write_text(json.dumps(store, indent=2), encoding="utf-8")
    except OSError as exc:
        return _err("service_unavailable", f"Could not persist draft: {exc}.",
                    tool="create_support_case")
    return {"case_id": cid, "status": "Pending", "category": args["category"],
            "subject": str(args["subject"]), "created_by": "agent_draft",
            "created_at": record["created"]}


# ------------------------------------------------------------- orchestrator ---
DISPATCH = {"get_timetable": get_timetable, "get_case_status": get_case_status,
            "search_knowledge_base": search_knowledge_base,
            "create_support_case": create_support_case}


def call_tool(tool_name: str, args: dict, session: dict) -> dict:
    """Single entry point the application/orchestration layer uses.

    The model may only choose (tool_name, args) from TOOL_SCHEMAS; all
    authorization and validation run here in deterministic code.
    """
    fn = DISPATCH.get(tool_name)
    if fn is None:
        return _err("unknown_tool", f"Unknown tool: {tool_name}.",
                    available=sorted(DISPATCH.keys()))
    try:
        result = fn(dict(args), dict(session))
    except Exception as exc:  # never let a tool crash the orchestrator
        return _err("tool_crashed", f"Tool {tool_name} failed unexpectedly: {exc}.",
                    tool=tool_name)
    if not isinstance(result, dict):
        return _err("malformed_response",
                    f"Tool {tool_name} returned a malformed response.",
                    tool=tool_name)
    result.setdefault("tool", tool_name)
    return result


def run_demo() -> None:
    session = {"student_id": "2300701330", "active_case_id": "CASE-1001"}
    demos = [
        ("get_timetable", {"student_id": "2300701330"}),
        ("get_case_status", {"case_id": "CASE-1001", "student_id": "2300701330"}),
        ("search_knowledge_base", {"query": "retake policy for failed courses"}),
        ("create_support_case", {"student_id": "2300701330", "category": "missing_marks",
                                 "subject": "Missing BSE4104 marks",
                                 "description": "Coursework mark not on portal."}),
    ]
    print(f"{'Tool':<22} {'Outcome':<60}")
    print("-" * 90)
    for name, args in demos:
        res = call_tool(name, args, session)
        if "error" in res:
            print(f"{name:<22} ERROR {res['error']}: {res['message'][:45]}")
        elif name == "get_timetable":
            print(f"{name:<22} {len(res.get('entries', []))} entries for {res.get('student_id')}")
        elif name == "get_case_status":
            print(f"{name:<22} {res.get('case_id')} status={res.get('status')}")
        elif name == "search_knowledge_base":
            print(f"{name:<22} {len(res.get('results', []))} results, top={res['results'][0]['doc_id'] if res.get('results') else 'none'}")
        else:
            print(f"{name:<22} draft {res.get('case_id')} status={res.get('status')}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--call", type=str, default=None)
    ap.add_argument("--args", type=str, default="{}")
    ap.add_argument("--session", type=str, default='{"student_id":"2300701330"}')
    a = ap.parse_args()
    if a.demo:
        run_demo()
    elif a.call:
        print(json.dumps(call_tool(a.call, json.loads(a.args), json.loads(a.session)), indent=2))
    else:
        ap.print_help()
