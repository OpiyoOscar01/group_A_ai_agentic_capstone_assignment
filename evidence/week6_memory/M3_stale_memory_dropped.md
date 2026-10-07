# M3 - A closed case is no longer treated as active

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
- **student (session B):** What is the status of my case?
- **agent:** Your last case CASE-0005 is now Resolved, so I no longer treat it as active. If you want to check another case, give me its ID.

## Checks

- PASS: reply says the case is Resolved and no longer active
- PASS: memory record deleted
- PASS: audit log records deletion reason case_closed

## Memory file at the end of the scenario (data/memory.json)

```json
{}
```

## Memory audit log (content-free)

- 20:16:54 2300701098 write CASE-0005 created
- 20:16:54 2300701098 read CASE-0005 hit
- 20:16:54 2300701098 delete CASE-0005 case_closed
