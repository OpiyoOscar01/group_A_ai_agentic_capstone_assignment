# M1 - Memory improves a legitimate task: status follow-up in 1 turn instead of 2, across a restart

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
- **student (baseline, no memory):** What is the status of my case?
- **agent:** I don't have an active case on record for you. Please tell me the case ID (format CASE-0000).
- **student (baseline, no memory):** Check status of CASE-0005
- **agent:** {"status": "ok", "data": {"case_id": "CASE-0005", "category": "missing_marks", "status": "Pending", "created_at": "2026-10-07T20:16:54.674516+00:00"}}
- **student (session B, next day):** What is the status of my case?
- **agent:** Your active case CASE-0005 (missing_marks) is Pending. I remembered it from your earlier request. Say "forget my session" to clear it.

## Checks

- PASS: memory record persisted to disk after the case was created
- PASS: baseline without memory had to ask for the case ID
- PASS: with memory the answer names the remembered case and its live status (Pending) in ONE turn
- PASS: turns needed (measured): 1 with memory < 2 without
- PASS: status shown came from a live lookup, not from stored text (record holds no status)

## Memory file at the end of the scenario (data/memory.json)

```json
{
  "2300701098": {
    "active_case_id": "CASE-0005",
    "source": "created",
    "set_at": "2026-10-07T20:16:54.679370+00:00",
    "expires_at": "2026-11-06T20:16:54.679370+00:00"
  }
}
```

## Memory audit log (content-free)

- 20:16:54 2300701098 write CASE-0005 created
- 20:16:54 2300701098 read CASE-0005 hit
