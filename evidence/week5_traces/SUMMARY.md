# Week 5 execution traces - summary

Scripted planner, fresh copy of `data/` per scenario, faults injected at the tool/planner boundary.

| ID | Expected | Actual | Iterations | Tool calls | Rejected proposals | Verdict |
|---|---|---|---|---|---|---|
| W5-T01 (headline) | GOAL_MET | GOAL_MET | 6 | 4 | 0 | PASS |
| W5-T02 (headline) | GOAL_MET | GOAL_MET | 6 | 5 | 0 | PASS |
| W5-T03 (headline) | DUPLICATE_FOUND | DUPLICATE_FOUND | 2 | 2 | 0 | PASS |
| W5-T04 | HANDOFF_BOUNDARY | HANDOFF_BOUNDARY | 0 | 0 | 0 | PASS |
| W5-T05 | PREREQUISITE_NOT_MET | PREREQUISITE_NOT_MET | 3 | 2 | 0 | PASS |
| W5-T06 | APPROVAL_DECLINED | APPROVAL_DECLINED | 4 | 2 | 0 | PASS |
| W5-T07 | TOOL_FAILURE | TOOL_FAILURE | 2 | 3 | 0 | PASS |
| W5-T08 | MAX_ITERATIONS | MAX_ITERATIONS | 8 | 0 | 8 | PASS |
| W5-T09 | UNAUTHORIZED | UNAUTHORIZED | 2 | 2 | 0 | PASS |
| W5-T10 | NO_SOURCE | NO_SOURCE | 1 | 1 | 0 | PASS |
| W5-T11 | GOAL_MET | GOAL_MET | 6 | 4 | 0 | PASS |
| W5-T12 | NEEDS_INFO | NEEDS_INFO | 5 | 2 | 0 | PASS |
| W5-T13 | GOAL_MET | GOAL_MET | 7 | 4 | 1 | PASS |
