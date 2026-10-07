# W5-T05 - Prerequisite: student has not seen the lecturer first (DOC-02) -> PREREQUISITE_NOT_MET

| Field | Value |
|---|---|
| Student (session) | 2300707270 |
| Planner | scripted-rule-planner-v1 |
| Expected stop reason | PREREQUISITE_NOT_MET |
| Actual stop reason | **PREREQUISITE_NOT_MET** |
| Iterations / tool calls / questions / planner calls / rejected | 3 / 2 / 1 / 4 / 0 (limits 8 / 6 / 3 / 10) |
| Case created | none |
| Verdict | **PASS** |

## Conversation

- **student:** My BSE4104 marks are missing.
- **agent:** (Question 1 of 3) To prepare your case I still need: whether you have already reported this to your course lecturer; how many days ago you reported it; the semester (e.g. 2026-S1); the lecturer's name; your proof of coursework/exam attendance (e.g. exam card, attendance sheet).
- **student:** I haven't spoken to the lecturer yet, semester 2026-S1.
- **agent:** Before a case can be filed, you must first report the problem to your course lecturer and, if it is still unresolved after 7 days, come back to file a case. [Source: DOC-02] No case was created.

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
| 19 | 3 | TURN | student: I haven't spoken to the lecturer yet, semester 2026-S1. |
| 20 | 3 | RESUME | {"from_status": "awaiting_answer"} |
| 21 | 3 | BOUNDARY CHECK | hit = None |
| 22 | 3 | COLLECT | {"semester": "2026-S1", "lecturer_contacted": false}; still missing: ['lecturer', 'attendance_proof'] |
| 23 | 3 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=['lecturer', 'attendance_proof'], approval=NONE, existing_cases_loaded=True, duplicate_of=None |
| 24 | 3 | PLAN | `finish` {"outcome": "PREREQUISITE_NOT_MET"} - policy requires a prior step the student has not done |
| 25 | 3 | VALIDATE | accepted |
| 26 | 3 | **STOP** | **PREREQUISITE_NOT_MET**  counters={"iterations": 3, "tool_calls": 2, "questions_asked": 1, "model_calls": 4, "rejected_proposals": 0} |

## Student-facing result

> Before a case can be filed, you must first report the problem to your course lecturer and, if it is still unresolved after 7 days, come back to file a case. [Source: DOC-02] No case was created.

## Success-criteria checks (contract section 1)

- SC-1: n/a (no draft shown)
- SC-2: PASS (no write attempted)
- SC-3: n/a (no case created)
- SC-4: PASS (nothing created)
- SC-5: PASS
