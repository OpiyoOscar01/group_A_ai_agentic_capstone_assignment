# W5-T13 - Recovery: one invalid planner proposal is rejected (costs an iteration); the run still completes

| Field | Value |
|---|---|
| Student (session) | 2300716574 |
| Planner | scripted-planner+injected-invalid-proposal |
| Expected stop reason | GOAL_MET |
| Actual stop reason | **GOAL_MET** |
| Iterations / tool calls / questions / planner calls / rejected | 7 / 4 / 2 / 9 / 1 (limits 8 / 6 / 3 / 10) |
| Case created | CASE-0005 |
| Verdict | **PASS** |

## Conversation

- **student:** My BSE4104 marks are missing.
- **agent:** (Question 1 of 3) To prepare your case I still need: whether you have already reported this to your course lecturer; how many days ago you reported it; the semester (e.g. 2026-S1); the lecturer's name; your proof of coursework/exam attendance (e.g. exam card, attendance sheet).
- **student:** I reported it to Dr Kato 10 days ago, semester 2026-S1.
- **agent:** (Question 2 of 3) To prepare your case I still need: your proof of coursework/exam attendance (e.g. exam card, attendance sheet).
- **student:** I have my exam card and the signed attendance sheet.
- **agent:** Here is the case I will submit for you:
  Name: Ogwal Richard
  Category: missing_marks
  Description: Missing marks for BSE4104 (2026-S1). Lecturer: Dr Kato. Reported to lecturer 10 days ago, unresolved. Proof of attendance: exam card.
  Sources: DOC-02, DOC-06
Submit this? (yes/no)
- **student:** yes
- **agent:** Your case CASE-0005 was created with status Pending and confirmed in the system. Department staff will review it. Sources used: DOC-02, DOC-06.

## Loop trace

| # | Iterations used | Step | What happened |
|---|---|---|---|
| 1 | 0 | TURN | student: My BSE4104 marks are missing. |
| 2 | 0 | BOUNDARY CHECK | hit = None |
| 3 | 0 | COLLECT | {"course_code": "BSE4104"}; still missing: ['lecturer_contacted', 'days_since_report', 'semester', 'lecturer', 'attendance_proof'] |
| 4 | 0 | SENSE | state: category=missing_marks, sources=[], missing=['lecturer_contacted', 'days_since_report', 'semester', 'lecturer', 'attendance_proof'], approval=NONE, existing_cases_loaded=False, duplicate_of=None |
| 5 | 0 | PLAN | `search_handbook` {"query": "missing marks procedure lecturer support case"} - need approved policy before anything else |
| 6 | 0 | VALIDATE | accepted |
| 7 | 1 | ACT | `search_handbook` {"query": "missing marks procedure lecturer support case"} |
| 8 | 1 | OBSERVE | {"status": "ok", "top_score": 0.4056, "hits": [{"doc_id": "DOC-02", "chunk_id": "DOC-02-C1", "score": 0.4056}, {"doc_id": "DOC-06", "chunk_id": "DOC-06-C1", "score": 0... |
| 9 | 1 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=['lecturer_contacted', 'days_since_report', 'semester', 'lecturer', 'attendance_proof'], approval=NONE, existing_cases_loaded=False, duplicate_of=None |
| 10 | 1 | PLAN | `lookup_case_or_timetable` {"query_type": "my_cases"} - check for an existing case before creating anything |
| 11 | 1 | VALIDATE | accepted |
| 12 | 2 | ACT | `lookup_case_or_timetable` {"query_type": "my_cases", "case_id": null} |
| 13 | 2 | OBSERVE | {"status": "ok", "data": {"cases": []}} |
| 14 | 2 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=['lecturer_contacted', 'days_since_report', 'semester', 'lecturer', 'attendance_proof'], approval=NONE, existing_cases_loaded=True, duplicate_of=None |
| 15 | 2 | PLAN | `send_email` {"to": "registrar@example.org"} - (injected fault) unapproved tool |
| 16 | 3 | VALIDATE | **REJECTED: UNKNOWN_ACTION:send_email** (iteration consumed) |
| 17 | 3 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=['lecturer_contacted', 'days_since_report', 'semester', 'lecturer', 'attendance_proof'], approval=NONE, existing_cases_loaded=True, duplicate_of=None |
| 18 | 3 | PLAN | `ask_student` {"question": "(Question 1 of 3) To prepare your case I still need: whether you have already reported this to your course lecturer; how many days ago you reported it; t... - required fields missing |
| 19 | 3 | VALIDATE | accepted |
| 20 | 4 | ACT | `ask_student` {"question": "(Question 1 of 3) To prepare your case I still need: whether you have already reported this to your course lecturer; how many days ago you reported it; t... |
| 21 | 4 | PAUSE | {"reason": "awaiting student reply", "questions_asked": 1} |
| 22 | 4 | TURN | student: I reported it to Dr Kato 10 days ago, semester 2026-S1. |
| 23 | 4 | RESUME | {"from_status": "awaiting_answer"} |
| 24 | 4 | BOUNDARY CHECK | hit = None |
| 25 | 4 | COLLECT | {"semester": "2026-S1", "lecturer": "Dr Kato", "lecturer_contacted": true, "days_since_report": 10}; still missing: ['attendance_proof'] |
| 26 | 4 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=['attendance_proof'], approval=NONE, existing_cases_loaded=True, duplicate_of=None |
| 27 | 4 | PLAN | `ask_student` {"question": "(Question 2 of 3) To prepare your case I still need: your proof of coursework/exam attendance (e.g. exam card, attendance sheet).", "fields": ["attendanc... - required fields missing |
| 28 | 4 | VALIDATE | accepted |
| 29 | 5 | ACT | `ask_student` {"question": "(Question 2 of 3) To prepare your case I still need: your proof of coursework/exam attendance (e.g. exam card, attendance sheet).", "fields": ["attendanc... |
| 30 | 5 | PAUSE | {"reason": "awaiting student reply", "questions_asked": 2} |
| 31 | 5 | TURN | student: I have my exam card and the signed attendance sheet. |
| 32 | 5 | RESUME | {"from_status": "awaiting_answer"} |
| 33 | 5 | BOUNDARY CHECK | hit = None |
| 34 | 5 | COLLECT | {"attendance_proof": "exam card"}; still missing: [] |
| 35 | 5 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=[], approval=NONE, existing_cases_loaded=True, duplicate_of=None |
| 36 | 5 | PLAN | `present_draft` {"category": "missing_marks", "description": "Missing marks for BSE4104 (2026-S1). Lecturer: Dr Kato. Reported to lecturer 10 days ago, unresolved. Proof of attendance... - all required fields collected |
| 37 | 5 | VALIDATE | accepted |
| 38 | 5 | ACT | `present_draft` {"name": "Ogwal Richard", "category": "missing_marks", "description": "Missing marks for BSE4104 (2026-S1). Lecturer: Dr Kato. Reported to lecturer 10 days ago, unreso... |
| 39 | 5 | PAUSE | {"reason": "AWAITING_APPROVAL"} |
| 40 | 5 | TURN | student: yes |
| 41 | 5 | RESUME | {"from_status": "awaiting_approval"} |
| 42 | 5 | APPROVAL | {"status": "APPROVED", "reply": "yes"} |
| 43 | 5 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=[], approval=APPROVED, existing_cases_loaded=True, duplicate_of=None |
| 44 | 5 | PLAN | `create_draft_support_case` {"name": "Ogwal Richard", "category": "missing_marks", "description": "Missing marks for BSE4104 (2026-S1). Lecturer: Dr Kato. Reported to lecturer 10 days ago, unreso... - student approved the exact draft |
| 45 | 5 | VALIDATE | accepted |
| 46 | 6 | ACT | `create_draft_support_case` {"name": "Ogwal Richard", "category": "missing_marks", "description": "Missing marks for BSE4104 (2026-S1). Lecturer: Dr Kato. Reported to lecturer 10 days ago, unreso... |
| 47 | 6 | OBSERVE | {"status": "draft_created", "case_id": "CASE-0005", "case_status": "Pending"} |
| 48 | 6 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=[], approval=APPROVED, existing_cases_loaded=True, duplicate_of=None |
| 49 | 6 | PLAN | `lookup_case_or_timetable` {"query_type": "case_status", "case_id": "CASE-0005"} - verify the created case exists |
| 50 | 6 | VALIDATE | accepted |
| 51 | 7 | ACT | `lookup_case_or_timetable` {"query_type": "case_status", "case_id": "CASE-0005"} |
| 52 | 7 | OBSERVE | {"status": "ok", "data": {"case_id": "CASE-0005", "category": "missing_marks", "status": "Pending", "created_at": "2026-10-06T08:54:12.477150+00:00"}} |
| 53 | 7 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=[], approval=APPROVED, existing_cases_loaded=True, duplicate_of=None |
| 54 | 7 | PLAN | `finish` {"outcome": "GOAL_MET"} - case created and confirmed by lookup |
| 55 | 7 | VALIDATE | accepted |
| 56 | 7 | **STOP** | **GOAL_MET**  counters={"iterations": 7, "tool_calls": 4, "questions_asked": 2, "model_calls": 9, "rejected_proposals": 1} |

## Student-facing result

> Your case CASE-0005 was created with status Pending and confirmed in the system. Department staff will review it. Sources used: DOC-02, DOC-06.

## Success-criteria checks (contract section 1)

- SC-1: PASS
- SC-2: PASS
- SC-3: PASS
- SC-4: PASS
- SC-5: PASS
