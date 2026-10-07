# I1 - The MCP-style specification agrees with the implementation

**Verdict: PASS**

## Conversation

## Checks

- PASS: manifest tools == the agent's tool actions
- PASS: search_handbook: model-visible args and required args match the validator
- PASS: search_handbook: student_id / approved are not model-visible
- PASS: lookup_case_or_timetable: model-visible args and required args match the validator
- PASS: lookup_case_or_timetable: student_id / approved are not model-visible
- PASS: create_draft_support_case: model-visible args and required args match the validator
- PASS: create_draft_support_case: student_id / approved are not model-visible
- PASS: category enum == code ALLOWED_CATEGORIES
- PASS: query_type enum == code AGENT_QUERY_TYPES
- PASS: description maxLength == code limit
- PASS: every documented error code exists in the tool code
- PASS: read-only hints: search and lookup read-only, create is not
- PASS: behaviour matches spec: create without host approval -> APPROVAL_DECLINED
- PASS: memory store is declared as not exposed

## Memory file at the end of the scenario (data/memory.json)

```json
{}
```

## Memory audit log (content-free)

