# Live Demonstration Guide

**Group A Day - University Student-Support Case Agent**
BSE4104 AI Agentic Capstone, Makerere University

This is the one-page presenter runbook. The full script, with expected answers and question
preparation, is `docs/week8/Week8_04_Demo_Script.pdf`.

---

## Before the room opens

1. From the repository root, start the interface:

   ```bat
   demo\run_demo.bat
   ```

   Or run `python src/web_ui.py`. The browser opens `http://127.0.0.1:7860/`.

2. Confirm the header says **Scripted planner**. Scripted mode is deterministic and needs no API key.
3. Click **1. Happy path**, approve the draft, confirm `CASE-0005` is `Pending`, then press
   **Reset demo data and conversation**.
4. Pre-open these evidence tabs:
   - `evidence/week7_eval/final/RESULTS.md`
   - `evidence/week3_15tests_traces/R14.json`
   - `evidence/week7_guardrails/SUMMARY.md`
   - `evidence/week7_failures/CATALOGUE_EVIDENCE.md`

---

## 12-minute run sheet

| Time | Action | Say |
|---|---|---|
| 0:00 | Framing | "A bounded agent for routine support; the model proposes, the host validates." |
| 1:30 | Scenario 1 | "Watch what it does before it creates anything." |
| 2:15 | Answer three turns | "It collects the procedure facts and cites DOC-02 and DOC-06." |
| 3:30 | Approve | "Nothing exists until a human approves. It creates a Pending case, not an approval." |
| 4:30 | Scenario 4 | "Memory holds only the active case reference, and it is revalidated." |
| 6:00 | Scenario 6 | "The supported phrase is 'forget my session'. It deletes the reference and refuses to invent a case." |
| 7:30 | Scenario 3 | "Fee waiver and grade change are outside the tool set. It hands off to a human." |
| 9:30 | Scenario 2 | "Grounded policy answer with provenance. Retrieval is 14/15, not 15/15." |
| 11:00 | R14 trace | "This is the failure that survives our process; we do not fix it live." |
| 12:30 | Evidence | "Results, one trace, guardrails, and the unverified-findings caveat." |

---

## Exact student turns

| Segment | Turn |
|---|---|
| Happy path | "My BSE4104 marks are missing." |
| Happy path | "I reported it to Dr Kato 10 days ago, semester 2026-S1." |
| Happy path | "I have my exam card and the signed attendance sheet." |
| Approval | Click **Approve and submit** (or type "yes") |
| Status | "What is the status of my case?" |
| Forget | "Forget my session." |
| Boundary | "I want to file a case asking the department to waive my tuition fee and change my grade for BSE4104." |
| Policy | "How many times can I retake a failed course?" |

---

## The R14 segment (important)

Do **not** type "Change my grade for BSE4104 from B to A." and expect the old wrong citation. The
final boundary layer refuses a grade change before retrieval, so that specific query is now handled
safely. Show `evidence/week3_15tests_traces/R14.json` instead.

The retained trace records the Week 3 failure: DOC-05 was the top passage at cosine 0.2228 and was
cited instead of abstaining (failure class F-03). The lexical weakness remains for unanswerable policy
questions that do not trigger a boundary keyword. The `MIN_COVER=2` guard passes 15/15 locally but is
deliberately unmerged because it was not part of the 49-scenario release run.

---

## Reset, fallback and troubleshooting

- **Reset:** the button restores `CASE-0001` to `CASE-0004` and clears the conversation.
- **Port busy:** the server tries the next free port and prints the URL; use the printed URL.
- **Browser fails:** `python src/agent.py --chat --student 2300701098` with the same turns.
- **Live model fails:** stay in scripted mode; it is the default and needs no key.
- **State looks wrong:** reset, then restart the script from the happy path.
- **Do not switch planners during the run.** The scripted planner is the verified demonstration path.
