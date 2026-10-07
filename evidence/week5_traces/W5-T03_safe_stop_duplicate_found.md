# W5-T03 - Safe stop: student already has a Pending case for this course -> DUPLICATE_FOUND

| Field | Value |
|---|---|
| Student (session) | 2300701330 |
| Planner | scripted-rule-planner-v1 |
| Expected stop reason | DUPLICATE_FOUND |
| Actual stop reason | **DUPLICATE_FOUND** |
| Iterations / tool calls / questions / planner calls / rejected | 2 / 2 / 0 / 3 / 0 (limits 8 / 6 / 3 / 10) |
| Case created | none |
| Verdict | **PASS** |

## Conversation

- **student:** I need to retake BIT2101
- **agent:** You already have a Pending case for this: CASE-0003. I did not create another one.

## Loop trace

| # | Iterations used | Step | What happened |
|---|---|---|---|
| 1 | 0 | TURN | student: I need to retake BIT2101 |
| 2 | 0 | BOUNDARY CHECK | hit = None |
| 3 | 0 | COLLECT | {"course_code": "BIT2101"}; still missing: ['semester'] |
| 4 | 0 | SENSE | state: category=retake, sources=[], missing=['semester'], approval=NONE, existing_cases_loaded=False, duplicate_of=None |
| 5 | 0 | PLAN | `search_handbook` {"query": "retake failed course policy"} - need approved policy before anything else |
| 6 | 0 | VALIDATE | accepted |
| 7 | 1 | ACT | `search_handbook` {"query": "retake failed course policy"} |
| 8 | 1 | OBSERVE | {"status": "ok", "top_score": 0.2444, "hits": [{"doc_id": "DOC-01", "chunk_id": "DOC-01-C1", "score": 0.2444}]} |
| 9 | 1 | SENSE | state: category=retake, sources=['DOC-01'], missing=['semester'], approval=NONE, existing_cases_loaded=False, duplicate_of=None |
| 10 | 1 | PLAN | `lookup_case_or_timetable` {"query_type": "my_cases"} - check for an existing case before creating anything |
| 11 | 1 | VALIDATE | accepted |
| 12 | 2 | ACT | `lookup_case_or_timetable` {"query_type": "my_cases", "case_id": null} |
| 13 | 2 | OBSERVE | {"status": "ok", "data": {"cases": [{"case_id": "CASE-0003", "category": "retake", "status": "Pending", "description": "Need to retake BIT2101.", "created_at": "2026-0... |
| 14 | 2 | SENSE | state: category=retake, sources=['DOC-01'], missing=['semester'], approval=NONE, existing_cases_loaded=True, duplicate_of=CASE-0003 |
| 15 | 2 | PLAN | `finish` {"outcome": "DUPLICATE_FOUND"} - student already has a Pending case for this |
| 16 | 2 | VALIDATE | accepted |
| 17 | 2 | **STOP** | **DUPLICATE_FOUND**  counters={"iterations": 2, "tool_calls": 2, "questions_asked": 0, "model_calls": 3, "rejected_proposals": 0} |

## Student-facing result

> You already have a Pending case for this: CASE-0003. I did not create another one.

## Success-criteria checks (contract section 1)

- SC-1: n/a (no draft shown)
- SC-2: PASS (no write attempted)
- SC-3: n/a (no case created)
- SC-4: PASS (nothing created)
- SC-5: PASS
