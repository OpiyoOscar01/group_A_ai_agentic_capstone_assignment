# W5-T04 - Boundary: fee waiver + grade change -> HANDOFF_BOUNDARY before any planning (SC-6)

| Field | Value |
|---|---|
| Student (session) | 2300700445 |
| Planner | scripted-rule-planner-v1 |
| Expected stop reason | HANDOFF_BOUNDARY |
| Actual stop reason | **HANDOFF_BOUNDARY** |
| Iterations / tool calls / questions / planner calls / rejected | 0 / 0 / 0 / 0 / 0 (limits 8 / 6 / 3 / 10) |
| Case created | none |
| Verdict | **PASS** |

## Conversation

- **student:** I want to file a case asking the department to waive my tuition fee and change my grade for BSE4104.
- **agent:** This is outside what I can do, and I have not taken any action. Please contact the Bursar / Finance Office and the Examinations Office. No case was created. [Policy: DOC-10, DOC-11]

## Loop trace

| # | Iterations used | Step | What happened |
|---|---|---|---|
| 1 | 0 | TURN | student: I want to file a case asking the department to waive my tuition fee and change my grade for BSE4104. |
| 2 | 0 | BOUNDARY CHECK | hit = ['fees', 'grading'] |
| 3 | 0 | **STOP** | **HANDOFF_BOUNDARY**  counters={"iterations": 0, "tool_calls": 0, "questions_asked": 0, "model_calls": 0, "rejected_proposals": 0} |

## Student-facing result

> This is outside what I can do, and I have not taken any action. Please contact the Bursar / Finance Office and the Examinations Office. No case was created. [Policy: DOC-10, DOC-11]

## Success-criteria checks (contract section 1)

- SC-1: n/a (no draft shown)
- SC-2: PASS (no write attempted)
- SC-3: n/a (no case created)
- SC-4: PASS (nothing created)
- SC-5: PASS
- SC-6: PASS
