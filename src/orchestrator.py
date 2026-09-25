"""
Week 4 - Orchestration layer (Application/Integration Lead: Ogwal Richard)
Decides, for a given student message, whether to answer from the RAG pipeline
(src/rag.py) or call one of the two tools (src/tools.py). Enforces the human
approval gate for create_draft_support_case in code, not just in the prompt.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tools  # noqa: E402
import rag    # noqa: E402


def route(student_id, message, pending_confirmation=None):
    """
    pending_confirmation: if the previous turn showed a draft case and asked
    "shall I submit this?", pass the drafted fields here plus the student's
    yes/no reply as message, to actually invoke the approval-gated tool.
    """
    low = message.lower()

    # --- Step 1: is this a confirmation of a previously shown draft? ---
    if pending_confirmation:
        if low.strip() in ("yes", "yes submit", "confirm", "submit"):
            result = tools.create_draft_support_case(**pending_confirmation, approved=True)
            return {"decision": "tool:create_draft_support_case", "tool_result": result,
                     "message": f"Case {result.get('case_id')} created with status Pending. "
                                 f"Staff will review it." if result.get("status") == "draft_created"
                                 else "I could not create the case. Please try again or visit the Department Office."}
        else:
            return {"decision": "tool:create_draft_support_case", "tool_result": {"status": "rejected", "error_code": "APPROVAL_DECLINED"},
                    "message": "No case was created. Let me know if you'd like to try again."}

    # --- Step 2: does this look like a case-status or timetable lookup? ---
    if "case" in low and ("status" in low or "case-" in low.upper() or "check" in low):
        case_id = next((w.upper() for w in message.split() if w.upper().startswith("CASE-")), None)
        result = tools.lookup_case_or_timetable(student_id, "case_status", case_id)
        return {"decision": "tool:lookup_case_or_timetable", "tool_result": result}

    if "timetable" in low or "schedule" in low or "class" in low:
        result = tools.lookup_case_or_timetable(student_id, "timetable")
        return {"decision": "tool:lookup_case_or_timetable", "tool_result": result}

    # --- Step 3: does this look like a request to open a new case? ---
    if "file a case" in low or "submit a case" in low or "create a case" in low or "report" in low:
        # In a full build the agent would extract category/description via the
        # LLM; here we simulate a drafted case awaiting approval.
        draft = {"student_id": student_id, "name": "Student", "category": "other",
                 "description": message}
        return {"decision": "await_approval", "draft": draft,
                "message": f"I'd like to submit this case: category='{draft['category']}', "
                            f"description='{draft['description']}'. Shall I submit it? (yes/no)"}

    # --- Step 4: fall back to the RAG pipeline (Week 3) ---
    rag_result = rag.answer(message)
    return {"decision": f"rag:{rag_result['decision']}", "rag_result": rag_result}


if __name__ == "__main__":
    sid = "2300701098"
    print("--- Timetable request ---")
    print(json.dumps(route(sid, "What's my class schedule this semester?"), indent=2))

    print("\n--- Case status request ---")
    print(json.dumps(route(sid, "Check status of CASE-0002"), indent=2))

    print("\n--- New case request (step 1: draft shown) ---")
    step1 = route(sid, "I want to file a case about a missing mark in BSE4104")
    print(json.dumps(step1, indent=2))

    print("\n--- New case request (step 2: student confirms) ---")
    step2 = route(sid, "yes", pending_confirmation=step1["draft"])
    print(json.dumps(step2, indent=2))

    print("\n--- Falls back to RAG ---")
    print(json.dumps(route(sid, "How many credit units can I register for?"), indent=2))
