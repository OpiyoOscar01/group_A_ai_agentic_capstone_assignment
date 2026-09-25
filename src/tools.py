"""
Week 4 - Tool implementations 
Implements the two tools defined in docs/architecture/Week4_01_Tool_Catalogue.docx:
  1. lookup_case_or_timetable   - read-only, no side effect, auto-approved
  2. create_draft_support_case  - side effect, requires human approval before invocation

Design rule carried from Week 1/3: "LLM suggests, deterministic software enforces."
Neither tool can ever move a case beyond "Pending", and neither touches
fee/admissions/grading/disciplinary decisions (see DOC-10, DOC-11).
"""
import json
import os
import re
import uuid
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

STUDENT_ID_RE = re.compile(r"^\d{10}$")
CASE_ID_RE = re.compile(r"^CASE-\d{4}$")
ALLOWED_CATEGORIES = {"missing_marks", "retake", "registration", "other"}


def _load(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return None  # simulates SERVICE_UNAVAILABLE
    with open(path) as f:
        return json.load(f)


def _save(name, obj):
    path = os.path.join(DATA, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


# ---------------------------------------------------------------------------
# Tool 1: lookup_case_or_timetable (read-only)
# ---------------------------------------------------------------------------
def lookup_case_or_timetable(student_id, query_type, case_id=None):
    if not STUDENT_ID_RE.match(str(student_id or "")):
        return {"status": "error", "error_code": "INVALID_ID"}
    if query_type not in ("case_status", "timetable"):
        return {"status": "error", "error_code": "INVALID_ID"}

    if query_type == "case_status":
        if not case_id or not CASE_ID_RE.match(case_id):
            return {"status": "error", "error_code": "INVALID_ID"}
        cases = _load("cases.json")
        if cases is None:
            return {"status": "error", "error_code": "SERVICE_UNAVAILABLE"}
        match = next((c for c in cases if c["case_id"] == case_id), None)
        if match is None:
            return {"status": "error", "error_code": "NOT_FOUND"}
        if match["student_id"] != student_id:
            return {"status": "error", "error_code": "UNAUTHORIZED"}
        return {"status": "ok", "data": {
            "case_id": match["case_id"], "category": match["category"],
            "status": match["status"], "created_at": match["created_at"]
        }}

    # query_type == "timetable"
    timetable = _load("timetable.json")
    if timetable is None:
        return {"status": "error", "error_code": "SERVICE_UNAVAILABLE"}
    match = next((t for t in timetable if t["student_id"] == student_id), None)
    if match is None:
        return {"status": "error", "error_code": "NOT_FOUND"}
    return {"status": "ok", "data": {"semester": match["semester"], "entries": match["entries"]}}


# ---------------------------------------------------------------------------
# Tool 2: create_draft_support_case (side effect - approval-gated)
# ---------------------------------------------------------------------------
BOUNDARY_HINTS = ["fee", "waiver", "admission", "eligib", "disciplinary", "grade", "grading"]


def create_draft_support_case(student_id, name, category, description, approved=False):
    # Approval gate: the orchestrator must have obtained explicit confirmation
    # before calling with approved=True. This mirrors the human-approval
    # requirement in the catalogue - it is enforced here, not just in the prompt.
    if not approved:
        return {"status": "rejected", "error_code": "APPROVAL_DECLINED"}

    values = {"student_id": student_id, "name": name, "category": category, "description": description}
    missing = [f for f, v in values.items() if not v]
    if missing:
        return {"status": "error", "error_code": "MISSING_FIELD", "missing_fields": missing}

    if not STUDENT_ID_RE.match(str(student_id)):
        return {"status": "error", "error_code": "MISSING_FIELD"}

    if category not in ALLOWED_CATEGORIES:
        return {"status": "error", "error_code": "INVALID_CATEGORY"}

    low = description.lower()
    if any(h in low for h in BOUNDARY_HINTS):
        # Deliberately refuse even if the caller mislabelled the category -
        # deterministic guard behind the LLM's own classification.
        return {"status": "error", "error_code": "INVALID_CATEGORY"}

    cases = _load("cases.json")
    if cases is None:
        return {"status": "error", "error_code": "SERVICE_UNAVAILABLE"}

    next_num = len(cases) + 1
    case_id = f"CASE-{next_num:04d}"
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "case_id": case_id, "student_id": student_id, "category": category,
        "name": name, "description": description, "status": "Pending",
        "created_by": "agent_draft", "created_at": now, "updated_at": now
    }
    cases.append(record)
    _save("cases.json", cases)
    return {"status": "draft_created", "case_id": case_id, "case_status": "Pending"}


# ---------------------------------------------------------------------------
# CLI demo - "Working demonstration of at least two tools"
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Tool 1: lookup_case_or_timetable ===")
    print("Case lookup (own case):",
          json.dumps(lookup_case_or_timetable("2300700445", "case_status", "CASE-0001")))
    print("Timetable lookup:",
          json.dumps(lookup_case_or_timetable("2300701098", "timetable")))

    print("\n=== Tool 2: create_draft_support_case ===")
    print("Blocked without approval:",
          json.dumps(create_draft_support_case("2300701330", "Opiyo Oscar", "retake",
                                                "Need to retake BIT2101.", approved=False)))
    print("Created after approval:",
          json.dumps(create_draft_support_case("2300701330", "Opiyo Oscar", "retake",
                                                "Need to retake BIT2101.", approved=True)))
