# M4 - Deletion on request works and is final

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
- **student (session B):** Please forget my session
- **agent:** Done. I no longer remember an active case for you.
- **student (session C):** What is the status of my case?
- **agent:** I don't have an active case on record for you. Please tell me the case ID (format CASE-0000).

## Checks

- PASS: student can delete the record on request
- PASS: after deletion the agent asks for the ID instead of guessing
- PASS: audit log records student_request deletion

## Memory file at the end of the scenario (data/memory.json)

```json
{}
```

## Memory audit log (content-free)

- 20:16:54 2300701098 write CASE-0005 created
- 20:16:54 2300701098 delete CASE-0005 student_request
- 20:16:54 2300701098 read None miss
