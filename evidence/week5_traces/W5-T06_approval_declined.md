# W5-T06 - Approval gate: student does not say an explicit yes -> APPROVAL_DECLINED, nothing created (SC-2)

| Field | Value |
|---|---|
| Student (session) | 2300716574 |
| Planner | scripted-rule-planner-v1 |
| Expected stop reason | APPROVAL_DECLINED |
| Actual stop reason | **APPROVAL_DECLINED** |
| Iterations / tool calls / questions / planner calls / rejected | 4 / 2 / 2 / 5 / 0 (limits 8 / 6 / 3 / 10) |
| Case created | none |
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
- **student:** no, the lecturer is wrong, let me fix it
- **agent:** Nothing was created. Tell me what to change and I will prepare a new draft.

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
| 8 | 1 | OBSERVE | {"status": "ok", "top_score": 0.4096, "hits": [{"doc_id": "DOC-02", "chunk_id": "DOC-02-C1", "score": 0.4096}, {"doc_id": "DOC-06", "chunk_id": "DOC-06-C1", "score": 0... |
| 9 | 1 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=['lecturer_contacted', 'days_since_report', 'semester', 'lecturer', 'attendance_proof'], approval=NONE, existing_cases_loaded=False, duplicate_of=None |
| 10 | 1 | PLAN | `lookup_case_or_timetable` {"query_type": "my_cases"} - check for an existing case before creating anything |
| 11 | 1 | VALIDATE | accepted |
| 12 | 2 | ACT | `lookup_case_or_timetable` {"query_type": "my_cases", "case_id": null} |
| 13 | 2 | OBSERVE | {"status": "ok", "data": {"cases": []}} |
| 14 | 2 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=['lecturer_contacted', 'days_since_report', 'semester', 'lecturer', 'attendance_proof'], approval=NONE, existing_cases_loaded=True, duplicate_of=None |
| 15 | 2 | PLAN | `ask_student` {"question": "(Question 1 of 3) To prepare your case I still need: whether you have already reported this to your course lecturer; how many days ago you reported it; t... - required fields missing |
| 16 | 2 | VALIDATE | accepted |
| 17 | 3 | ACT | `ask_student` {"question": "(Question 1 of 3) To prepare your case I still need: whether you have already reported this to your course lecturer; how many days ago you reported it; t... |
| 18 | 3 | PAUSE | {"reason": "awaiting student reply", "questions_asked": 1} |
| 19 | 3 | TURN | student: I reported it to Dr Kato 10 days ago, semester 2026-S1. |
| 20 | 3 | RESUME | {"from_status": "awaiting_answer"} |
| 21 | 3 | BOUNDARY CHECK | hit = None |
| 22 | 3 | COLLECT | {"semester": "2026-S1", "lecturer": "Dr Kato", "lecturer_contacted": true, "days_since_report": 10}; still missing: ['attendance_proof'] |
| 23 | 3 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=['attendance_proof'], approval=NONE, existing_cases_loaded=True, duplicate_of=None |
| 24 | 3 | PLAN | `ask_student` {"question": "(Question 2 of 3) To prepare your case I still need: your proof of coursework/exam attendance (e.g. exam card, attendance sheet).", "fields": ["attendanc... - required fields missing |
| 25 | 3 | VALIDATE | accepted |
| 26 | 4 | ACT | `ask_student` {"question": "(Question 2 of 3) To prepare your case I still need: your proof of coursework/exam attendance (e.g. exam card, attendance sheet).", "fields": ["attendanc... |
| 27 | 4 | PAUSE | {"reason": "awaiting student reply", "questions_asked": 2} |
| 28 | 4 | TURN | student: I have my exam card and the signed attendance sheet. |
| 29 | 4 | RESUME | {"from_status": "awaiting_answer"} |
| 30 | 4 | BOUNDARY CHECK | hit = None |
| 31 | 4 | COLLECT | {"attendance_proof": "exam card"}; still missing: [] |
| 32 | 4 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=[], approval=NONE, existing_cases_loaded=True, duplicate_of=None |
| 33 | 4 | PLAN | `present_draft` {"category": "missing_marks", "description": "Missing marks for BSE4104 (2026-S1). Lecturer: Dr Kato. Reported to lecturer 10 days ago, unresolved. Proof of attendance... - all required fields collected |
| 34 | 4 | VALIDATE | accepted |
| 35 | 4 | ACT | `present_draft` {"name": "Ogwal Richard", "category": "missing_marks", "description": "Missing marks for BSE4104 (2026-S1). Lecturer: Dr Kato. Reported to lecturer 10 days ago, unreso... |
| 36 | 4 | PAUSE | {"reason": "AWAITING_APPROVAL"} |
| 37 | 4 | TURN | student: no, the lecturer is wrong, let me fix it |
| 38 | 4 | RESUME | {"from_status": "awaiting_approval"} |
| 39 | 4 | APPROVAL | {"status": "DECLINED", "reply": "no, the lecturer is wrong, let me fix it"} |
| 40 | 4 | **STOP** | **APPROVAL_DECLINED**  counters={"iterations": 4, "tool_calls": 2, "questions_asked": 2, "model_calls": 5, "rejected_proposals": 0} |

## Student-facing result

> Nothing was created. Tell me what to change and I will prepare a new draft.

## Success-criteria checks (contract section 1)

- SC-1: PASS
- SC-2: PASS (no write attempted)
- SC-3: n/a (no case created)
- SC-4: PASS (nothing created)
- SC-5: PASS
