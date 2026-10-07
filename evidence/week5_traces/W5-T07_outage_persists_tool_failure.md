# W5-T07 - Failure: outage persists after the one retry -> TOOL_FAILURE, no partial record

| Field | Value |
|---|---|
| Student (session) | 2300701098 |
| Planner | scripted-rule-planner-v1 |
| Expected stop reason | TOOL_FAILURE |
| Actual stop reason | **TOOL_FAILURE** |
| Iterations / tool calls / questions / planner calls / rejected | 2 / 3 / 0 / 2 / 0 (limits 8 / 6 / 3 / 10) |
| Case created | none |
| Verdict | **PASS** |

## Conversation

- **student:** My BSE4104 marks are missing.
- **agent:** The service is unavailable right now. Please try later or visit the Department Office. No case was created.

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
| 13 | 2 | OBSERVE | {"status": "error", "error_code": "SERVICE_UNAVAILABLE"} |
| 14 | 2 | RETRY | {"action": "lookup_case_or_timetable", "reason": "SERVICE_UNAVAILABLE", "retry_no": 1} |
| 15 | 2 | ACT | `lookup_case_or_timetable` {"query_type": "my_cases", "case_id": null} |
| 16 | 2 | OBSERVE | {"status": "error", "error_code": "SERVICE_UNAVAILABLE"} |
| 17 | 2 | **STOP** | **TOOL_FAILURE** (SERVICE_UNAVAILABLE after one retry) counters={"iterations": 2, "tool_calls": 3, "questions_asked": 0, "model_calls": 2, "rejected_proposals": 0} |

## Student-facing result

> The service is unavailable right now. Please try later or visit the Department Office. No case was created.

## Success-criteria checks (contract section 1)

- SC-1: n/a (no draft shown)
- SC-2: PASS (no write attempted)
- SC-3: n/a (no case created)
- SC-4: PASS (nothing created)
- SC-5: PASS
