# W5-T10 - Grounding: no approved source supports the request -> NO_SOURCE

| Field | Value |
|---|---|
| Student (session) | 2300700445 |
| Planner | scripted-rule-planner-v1 |
| Expected stop reason | NO_SOURCE |
| Actual stop reason | **NO_SOURCE** |
| Iterations / tool calls / questions / planner calls / rejected | 1 / 1 / 0 / 2 / 0 (limits 8 / 6 / 3 / 10) |
| Case created | none |
| Verdict | **PASS** |

## Conversation

- **student:** I want to file a case about my parking permit
- **agent:** I don't know this from approved documents. Please visit the Department Office. No case was created.

## Loop trace

| # | Iterations used | Step | What happened |
|---|---|---|---|
| 1 | 0 | TURN | student: I want to file a case about my parking permit |
| 2 | 0 | BOUNDARY CHECK | hit = None |
| 3 | 0 | SENSE | state: category=other, sources=[], missing=[], approval=NONE, existing_cases_loaded=False, duplicate_of=None |
| 4 | 0 | PLAN | `search_handbook` {"query": "I want to file a case about my parking permit"} - need approved policy before anything else |
| 5 | 0 | VALIDATE | accepted |
| 6 | 1 | ACT | `search_handbook` {"query": "I want to file a case about my parking permit"} |
| 7 | 1 | OBSERVE | {"status": "ok", "top_score": 0.1676, "hits": [{"doc_id": "DOC-02", "chunk_id": "DOC-02-C1", "score": 0.1676}]} |
| 8 | 1 | NOTE | {"note": "top score 0.1676 below stricter bar 0.25 for category 'other'"} |
| 9 | 1 | SENSE | state: category=other, sources=[], missing=[], approval=NONE, existing_cases_loaded=False, duplicate_of=None |
| 10 | 1 | PLAN | `finish` {"outcome": "NO_SOURCE"} - no approved source supports this request |
| 11 | 1 | VALIDATE | accepted |
| 12 | 1 | **STOP** | **NO_SOURCE**  counters={"iterations": 1, "tool_calls": 1, "questions_asked": 0, "model_calls": 2, "rejected_proposals": 0} |

## Student-facing result

> I don't know this from approved documents. Please visit the Department Office. No case was created.

## Success-criteria checks (contract section 1)

- SC-1: n/a (no draft shown)
- SC-2: PASS (no write attempted)
- SC-3: n/a (no case created)
- SC-4: PASS (nothing created)
- SC-5: PASS
