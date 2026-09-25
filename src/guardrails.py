"""Week 4 Safety layer – University Student-Support Case Agent.
Owner: Ogwal Richard (Application/Integration Lead).

Covers, on top of Oscar's src/tools.py:
  1. Authorization checks for every tool call (session-bound identity).
  2. Failure behaviour: invalid args, unauthorized, not-found, unavailable
     services, malformed/unexpected tool responses.
  3. Human approval before the one higher-impact action (create_support_case).
     The draft is held in data/approvals.json as PENDING_APPROVAL and only
     written to data/cases.json when a human approves. No auto-approval path.
  4. Evidence logging for Christine's test report.

Run:
  python src/guardrails.py --demo
  python src/guardrails.py --request-approval --student 2300701330 --category missing_marks --subject "T" --description "D"
  python src/guardrails.py --approve APR-0001 --approver "staff@makerere.ac.ug"
  python src/guardrails.py --list
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
APPROVALS_FILE = BASE / "data" / "approvals.json"
CASES_FILE = BASE / "data" / "cases.json"
AUDIT_FILE = BASE / "evidence" / "traces" / "guardrail_audit.jsonl"

sys.path.insert(0, str(BASE / "src"))
from tools import TOOL_SCHEMAS, VALID_CATEGORIES, call_tool, _now_iso  # noqa: E402


def _audit(event: dict) -> None:
    try:
        AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": _now_iso(), **event}) + "\n")
    except OSError:
        pass


def authorize(tool_name: str, args: dict, session: dict) -> str | None:
    """Return None if authorized, else a refusal reason. Runs before any tool."""
    if tool_name not in TOOL_SCHEMAS:
        return f"Unknown tool: {tool_name}. No such capability exists."
    sid = str(session.get("student_id", ""))
    if not re.fullmatch(r"^[0-9]{10}$", sid):
        return "No authenticated student session. Please provide your student ID first."
    if tool_name in ("get_timetable", "get_case_status", "create_support_case"):
        # Missing student_id is a schema problem, not an auth problem:
        # let validation report it precisely.
        if "student_id" not in args or args.get("student_id") in (None, ""):
            return None
        if str(args.get("student_id", "")) != sid:
            return ("Authorization failed: student_id does not match the authenticated "
                    "session. Cross-student access is never permitted.")
    if tool_name == "get_case_status":
        try:
            store = json.loads(CASES_FILE.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return None  # availability handled downstream, not here
        rec = store.get(str(args.get("case_id", "")).upper())
        if rec is not None and str(rec.get("student_id", "")) != sid:
            return ("Authorization failed: you may only query cases you own. "
                    "This attempt has been logged as a boundary event.")
    return None


USER_MESSAGE = {
    "invalid_arguments": "I need a bit more detail before I can do that. {detail}",
    "unauthorized": "I can't do that for another student's record. {detail}",
    "not_found": "I can't find that record for your student ID. Please confirm the ID and try again.",
    "service_unavailable": "That service is temporarily unavailable. Please try again later — nothing was changed.",
    "malformed_response": "I got an unexpected result from a tool, so I stopped instead of guessing. Staff have been notified.",
    "unknown_tool": "That action is not something I can do. I have not taken any action.",
    "pending_approval": "Your case draft {case_ref} is saved as PENDING_APPROVAL. A staff member must approve it before it becomes a case. Nothing else was changed.",
}


def validate_tool_response(tool_name: str, result: dict) -> str | None:
    """Second line of defense: check the tool's own output shape."""
    if not isinstance(result, dict):
        return "Tool returned a non-object."
    if "error" in result:
        return None  # error envelopes are always well-formed by construction
    if tool_name == "get_timetable":
        if not isinstance(result.get("entries"), list):
            return "get_timetable.entries is not a list."
    elif tool_name == "get_case_status":
        if result.get("status") not in ("Pending", "In Progress", "Resolved", "Rejected"):
            return f"Unexpected status value: {result.get('status')!r}."
    elif tool_name == "search_knowledge_base":
        if not isinstance(result.get("results"), list):
            return "search_knowledge_base.results is not a list."
    elif tool_name == "create_support_case":
        if result.get("status") != "Pending" or result.get("created_by") != "agent_draft":
            return "create_support_case returned a non-draft record."
    return None


def _load_approvals() -> dict:
    try:
        return json.loads(APPROVALS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_approvals(data: dict) -> None:
    APPROVALS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _next_approval_id(store: dict) -> str:
    nums = [int(re.search(r"(\d+)", k).group(1)) for k in store.keys()
            if re.fullmatch(r"APR-\d{4}", k)]
    return f"APR-{(max(nums) + 1) if nums else 1:04d}"


def guarded_call(tool_name: str, args: dict, session: dict) -> dict:
    """Full Richard safety pipeline: authorize -> approval-gate -> tool -> validate."""
    # 0. Unknown tools fail fast with their own code (no such capability).
    if tool_name not in TOOL_SCHEMAS:
        return {"error": "unknown_tool",
                "message": f"Unknown tool: {tool_name}. No such capability exists.",
                "tool": tool_name,
                "user_message": USER_MESSAGE["unknown_tool"]}
    # 1. Authorization next (before the tool ever sees the call)
    refusal = authorize(tool_name, args, session)
    if refusal:
        _audit({"event": "auth_refusal", "tool": tool_name, "reason": refusal[:120]})
        return {"error": "unauthorized", "message": refusal, "tool": tool_name,
                "user_message": USER_MESSAGE["unauthorized"].format(detail=refusal)}

    # 2. Human-approval gate for the one write action.
    # Validate arguments BEFORE holding anything, so malformed drafts
    # are rejected immediately instead of entering the approval queue.
    if tool_name == "create_support_case":
        from tools import validate_args as _validate
        schema_problem = _validate(tool_name, args)
        if schema_problem:
            return {"error": "invalid_arguments", "message": schema_problem,
                    "tool": tool_name,
                    "user_message": USER_MESSAGE["invalid_arguments"].format(
                        detail=schema_problem)}
        approvals = _load_approvals()
        aid = _next_approval_id(approvals)
        approvals[aid] = {"approval_id": aid, "state": "PENDING_APPROVAL",
                          "tool": tool_name, "args": dict(args),
                          "requested_by": str(session.get("student_id", "")),
                          "requested_at": _now_iso(), "decided_by": None,
                          "decided_at": None}
        try:
            _save_approvals(approvals)
        except OSError as exc:
            return {"error": "service_unavailable",
                    "message": f"Could not record approval request: {exc}.",
                    "tool": tool_name,
                    "user_message": USER_MESSAGE["service_unavailable"]}
        _audit({"event": "approval_requested", "approval_id": aid,
                "student": str(session.get("student_id", ""))})
        return {"approval_id": aid, "state": "PENDING_APPROVAL", "tool": tool_name,
                "message": f"Draft held for human approval as {aid}.",
                "user_message": USER_MESSAGE["pending_approval"].format(case_ref=aid)}

    # 3. Read tools go straight through Oscar's layer
    result = call_tool(tool_name, args, session)

    # 4. Validate the tool's own response shape
    if "error" not in result:
        shape_problem = validate_tool_response(tool_name, result)
        if shape_problem:
            _audit({"event": "malformed_response", "tool": tool_name,
                    "reason": shape_problem})
            return {"error": "malformed_response", "message": shape_problem,
                    "tool": tool_name,
                    "user_message": USER_MESSAGE["malformed_response"]}

    # 5. Attach user-safe wording for error envelopes
    if "error" in result:
        code = result["error"]
        template = USER_MESSAGE.get(code, "{detail}")
        try:
            result["user_message"] = template.format(detail=result.get("message", ""),
                                                     case_ref=result.get("case_id", ""))
        except (KeyError, IndexError):
            result["user_message"] = result.get("message", "")
    return result


def approve(approval_id: str, approver: str) -> dict:
    """Human-only step. There is deliberately no auto-approve path anywhere."""
    aid = str(approval_id).upper()
    approvals = _load_approvals()
    rec = approvals.get(aid)
    if rec is None:
        return {"error": "not_found", "message": f"No approval request {aid}."}
    if rec.get("state") != "PENDING_APPROVAL":
        return {"error": "invalid_arguments",
                "message": f"Request {aid} is already {rec.get('state')}."}
    # Execute the held write through Oscar's tool (status still locked Pending)
    session = {"student_id": rec["args"].get("student_id", "")}
    result = call_tool("create_support_case", rec["args"], session)
    if "error" in result:
        return result
    rec.update({"state": "APPROVED", "decided_by": approver,
                "decided_at": _now_iso(), "case_id": result.get("case_id")})
    _save_approvals(approvals)
    _audit({"event": "approval_granted", "approval_id": aid,
            "approver": approver, "case_id": result.get("case_id")})
    return {"approval_id": aid, "state": "APPROVED", "case_id": result.get("case_id"),
            "status": "Pending", "decided_by": approver}


def reject(approval_id: str, approver: str, reason: str = "") -> dict:
    aid = str(approval_id).upper()
    approvals = _load_approvals()
    rec = approvals.get(aid)
    if rec is None:
        return {"error": "not_found", "message": f"No approval request {aid}."}
    if rec.get("state") != "PENDING_APPROVAL":
        return {"error": "invalid_arguments",
                "message": f"Request {aid} is already {rec.get('state')}."}
    rec.update({"state": "REJECTED", "decided_by": approver,
                "decided_at": _now_iso(), "reject_reason": reason})
    _save_approvals(approvals)
    _audit({"event": "approval_rejected", "approval_id": aid, "approver": approver})
    return {"approval_id": aid, "state": "REJECTED"}


def run_demo() -> None:
    session = {"student_id": "2300701330"}
    print(f"{'Scenario':<34} {'Outcome'}")
    print("-" * 90)
    r = guarded_call("get_timetable", {"student_id": "2300701330"}, session)
    print(f"{'normal timetable lookup':<34} {len(r.get('entries', []))} entries")
    r = guarded_call("get_case_status", {"case_id": "CASE-1002", "student_id": "2300701330"}, session)
    print(f"{'cross-student case lookup':<34} {r.get('error')}: refused")
    r = guarded_call("create_support_case",
                     {"student_id": "2300701330", "category": "missing_marks",
                      "subject": "Demo draft"}, session)
    print(f"{'missing/invalid params':<34} {r.get('error')}: {r.get('message', '')[:45]}")
    r = guarded_call("search_knowledge_base", {"query": "x"}, session)
    print(f"{'malformed query':<34} {r.get('error')}: validation before tool runs")
    r = guarded_call("approve_case", {}, session)
    print(f"{'nonexistent tool call':<34} {r.get('error')}: no such capability")
    r = guarded_call("create_support_case",
                     {"student_id": "2300701330", "category": "missing_marks",
                      "subject": "Demo draft", "description": "Held for approval."}, session)
    print(f"{'write without approval':<34} held as {r.get('approval_id')} ({r.get('state')})")
    a = approve(r["approval_id"], "staff@makerere.ac.ug")
    print(f"{'human approval':<34} {a.get('state')} -> case {a.get('case_id')}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--request-approval", action="store_true")
    ap.add_argument("--approve", type=str, default=None)
    ap.add_argument("--approver", type=str, default="staff@makerere.ac.ug")
    ap.add_argument("--student", type=str, default="2300701330")
    ap.add_argument("--category", type=str, default="missing_marks")
    ap.add_argument("--subject", type=str, default="Demo draft")
    ap.add_argument("--description", type=str, default="Held for human approval.")
    a = ap.parse_args()
    if a.demo:
        run_demo()
    elif a.list:
        print(json.dumps(_load_approvals(), indent=2))
    elif a.request_approval:
        print(json.dumps(guarded_call(
            "create_support_case",
            {"student_id": a.student, "category": a.category,
             "subject": a.subject, "description": a.description},
            {"student_id": a.student}), indent=2))
    elif a.approve:
        print(json.dumps(approve(a.approve, a.approver), indent=2))
    else:
        ap.print_help()
