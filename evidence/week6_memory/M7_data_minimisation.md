# M7 - Only the justified field is stored

**Verdict: PASS**

## Conversation

- **student (session A):** My BSE4104 marks are missing.
- **agent:** (Question 1 of 3) To prepare your case I still need: whether you have already reported this to your course lecturer; how many days ago you reported it; the semester (e.g. 2026-S1); the lecturer's name; your proof of coursework/exam attendance (e.g. exam card, attendance sheet).
- **student (session A):** I reported it to Dr Kato 10 days ago, semester 2026-S1.
- **agent:** (Question 2 of 3) To prepare your case I still need: your proof of coursework/exam attendance (e.g. exam card, attendance sheet).
- **student (session A):** I have my exam card and the signed attendance sheet.
- **agent:** Here is the case I will submit for you:
  Name: Namatovu Christine Maria
  Category: missing_marks
  Description: Missing marks for BSE4104 (2026-S1). Lecturer: Dr Kato. Reported to lecturer 10 days ago, unresolved. Proof of attendance: exam card.
  Sources: DOC-02, DOC-06
Submit this? (yes/no)
- **student (session A):** yes
- **agent:** Your case CASE-0005 was created with status Pending and confirmed in the system. Department staff will review it. Sources used: DOC-02, DOC-06.

## Checks

- PASS: stored record has exactly the 4 allowed fields
- PASS: no free text stored (no name, description, course code, message text or draft)
- PASS: audit log lines contain no content fields
- PASS: no model-callable action touches memory (the six allowed actions are fixed)
- PASS: the ONLY call site that writes memory is the controller's _remember helper (agent.py)

## Memory file at the end of the scenario (data/memory.json)

```json
{
  "2300701098": {
    "active_case_id": "CASE-0005",
    "source": "created",
    "set_at": "2026-10-07T20:16:54.904205+00:00",
    "expires_at": "2026-11-06T20:16:54.904205+00:00"
  }
}
```

## Memory audit log (content-free)

- 20:16:54 2300701098 write CASE-0005 created
