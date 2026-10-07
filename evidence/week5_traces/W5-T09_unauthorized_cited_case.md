# W5-T09 - Identity: student cites another student's case -> UNAUTHORIZED, no details leaked

| Field | Value |
|---|---|
| Student (session) | 2300701330 |
| Planner | scripted-rule-planner-v1 |
| Expected stop reason | UNAUTHORIZED |
| Actual stop reason | **UNAUTHORIZED** |
| Iterations / tool calls / questions / planner calls / rejected | 2 / 2 / 0 / 2 / 0 (limits 8 / 6 / 3 / 10) |
| Case created | none |
| Verdict | **PASS** |

## Conversation

- **student:** I want to file a case about my marks. It is the same as CASE-0001.
- **agent:** I can't use or show that record. Nothing was changed.

## Loop trace

| # | Iterations used | Step | What happened |
|---|---|---|---|
| 1 | 0 | TURN | student: I want to file a case about my marks. It is the same as CASE-0001. |
| 2 | 0 | BOUNDARY CHECK | hit = None |
| 3 | 0 | COLLECT | {}; still missing: ['lecturer_contacted', 'days_since_report', 'course_code', 'semester', 'lecturer', 'attendance_proof'] |
| 4 | 0 | SENSE | state: category=missing_marks, sources=[], missing=['lecturer_contacted', 'days_since_report', 'course_code', 'semester', 'lecturer', 'attendance_proof'], approval=NONE, existing_cases_loaded=False, duplicate_of=None |
| 5 | 0 | PLAN | `search_handbook` {"query": "missing marks procedure lecturer support case"} - need approved policy before anything else |
| 6 | 0 | VALIDATE | accepted |
| 7 | 1 | ACT | `search_handbook` {"query": "missing marks procedure lecturer support case"} |
| 8 | 1 | OBSERVE | {"status": "ok", "top_score": 0.4096, "hits": [{"doc_id": "DOC-02", "chunk_id": "DOC-02-C1", "score": 0.4096}, {"doc_id": "DOC-06", "chunk_id": "DOC-06-C1", "score": 0... |
| 9 | 1 | SENSE | state: category=missing_marks, sources=['DOC-02', 'DOC-06'], missing=['lecturer_contacted', 'days_since_report', 'course_code', 'semester', 'lecturer', 'attendance_proof'], approval=NONE, existing_cases_loaded=False, duplicate_of=None |
| 10 | 1 | PLAN | `lookup_case_or_timetable` {"query_type": "case_status", "case_id": "CASE-0001"} - student cited a case; check it is theirs |
| 11 | 1 | VALIDATE | accepted |
| 12 | 2 | ACT | `lookup_case_or_timetable` {"query_type": "case_status", "case_id": "CASE-0001"} |
| 13 | 2 | OBSERVE | {"status": "error", "error_code": "UNAUTHORIZED"} |
| 14 | 2 | **STOP** | **UNAUTHORIZED**  counters={"iterations": 2, "tool_calls": 2, "questions_asked": 0, "model_calls": 2, "rejected_proposals": 0} |

## Student-facing result

> I can't use or show that record. Nothing was changed.

## Success-criteria checks (contract section 1)

- SC-1: n/a (no draft shown)
- SC-2: PASS (no write attempted)
- SC-3: n/a (no case created)
- SC-4: PASS (nothing created)
- SC-5: PASS
