# University Student-Support Case Agent - Group A Day (BSE4104)

A bounded AI agent that helps university students resolve routine support problems. It answers
questions from a controlled corpus with citations, looks up case and timetable records through typed
tools, and drafts a support case that is created **only after the student explicitly approves it**.

Built for **BSE4104 Emerging Trends in Software Engineering**, Makerere University - Group A Day.

> **Safety boundary in one line:** the model may propose; the host validates and executes. Fee
> decisions, academic-record changes and emergency actions are refused and handed to a human.

---

## Demo quick start

The demonstration interface has no third-party dependencies and no API key requirement in scripted
mode.

```bash
git clone https://github.com/OpiyoOscar01/group_A_ai_agentic_capstone_assignment.git
cd group_A_ai_agentic_capstone_assignment
python src/web_ui.py
```

Open `http://127.0.0.1:7860/`. Use the six scenario buttons, approve the draft, then inspect the run.
Press **Reset demo data and conversation** between independent segments.

Optional live Gemini planner:

```bash
pip install -r requirements.txt
set GEMINI_API_KEY=your-key-here        # Windows
python src/web_ui.py --planner gemini
```

Terminal fallback, same agent:

```bash
python src/agent.py --chat --student 2300701098
```

The interface follows the Custosell design system: `blue-600`
primary actions, a `gray-50` canvas, white 16px cards, 8px control radii, restrained shadows and a
system sans stack. It is implemented as dependency-free HTML/CSS so the demo remains reproducible on
a clean machine.

---

## What it does

| Capability | Behaviour |
|---|---|
| Policy questions | Grounded answer with a source identifier and section, or an honest abstention |
| Partial questions | States what is supported and what is missing |
| Case / timetable lookup | Typed tool call with an ownership check |
| Case creation | Draft, explicit approval, then a `Pending` case |
| Out-of-scope requests | Refusal with a handoff message; no tool exists for fee or record decisions |
| Follow-up turns | Resumes the active case reference (30-day TTL) and can forget it on request |

The agent asks at most three clarifying questions, takes at most eight iterations and six tool calls,
and records a full trace for every run.

---

## Architecture

```
Browser UI (src/web_ui.py)  or  CLI (src/agent.py)
    |
    +-- Retrieval (src/rag.py)             TF-IDF + cosine, top-3, min score 0.14
    +-- Orchestrator (src/orchestrator.py) intent routing + approval gate
    +-- Agent loop (src/agent.py)          plan -> validate -> act -> observe -> stop
    +-- Tools (src/tools.py)               search_handbook, lookup_case_or_timetable,
    |                                      create_draft_support_case
    +-- Memory (src/memory.py)             active_case_id only, TTL 30 days, audit log
```

Model: **Gemini 2.0 Flash** (structured JSON / function calling). Prompts are versioned in `prompts/`
(`v1.0`, `v1.1`, `v2.0`, `v3.0-rag`). The default demonstration planner is a deterministic scripted
policy; the live model is optional.

Architecture diagrams: [`docs/architecture/`](../docs/architecture/).

---

## Requirements

- Python 3.11 or newer
- No third-party packages for the browser UI and scripted agent
- A Gemini API key only for the optional live planner

---

## Configuration

Copy `.env.example` to `.env` and set the key. **Never commit `.env`.**

```ini
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.0-flash
```

`.env` is excluded by `.gitignore`. The application reads configuration from the environment only.

---

## Evaluation and evidence

The evaluation harnesses live under **`tests/`**. All commands run from the repository root.

```bash
# 49-scenario end-to-end evaluation (scripted planner, deterministic)
python tests/run_week7_eval.py --label final

# 16 adversarial guardrail probes
python tests/run_week7_guardrails.py

# 13 agent workflow traces
python tests/run_week5_agent_traces.py

# 8 memory scenarios
python tests/run_week6_memory_demo.py

# Failure-catalogue re-tests
python tests/retest_failures.py
```

Retained results:

| Evidence | Result | Location |
|---|---|---|
| End-to-end | 49/49 (100%) | `evidence/week7_eval/final/RESULTS.md` |
| Guardrails | 16/16 | `evidence/week7_guardrails/SUMMARY.md` |
| Memory | 8/8 | `evidence/week6_memory/SUMMARY.md` |
| Agent traces | 13/13 | `evidence/week5_traces/SUMMARY.md` |
| Retrieval | 14/15 (93%) | Week 3 deliverable |
| Traceability | 39/39 | Week 7 evidence |

Latency in the retained final run: p50 1.9 ms, p95 32.6 ms, max 57.0 ms (budget 2,000 ms).
These are **scripted-planner orchestration times**, not live model latency.

---

## Repository structure

```
|
+-- src/
|   +-- web_ui.py           # dependency-free browser demonstration UI
|   +-- app.py              # Week 2 CLI baseline
|   +-- rag.py              # corpus loading, chunking, retrieval, grounding
|   +-- orchestrator.py     # routing and approval gate
|   +-- agent.py            # bounded planner loop, validation, stop conditions
|   +-- tools.py            # typed tools and schemas
|   +-- memory.py           # minimal active-case memory
+-- prompts/                # v1.0, v1.1, v2.0, v3.0-rag
+-- tools_schemas/          # JSON schemas for each tool
+-- tests/                  # evaluation harnesses and scenario sets
+-- evidence/               # retained results, traces, failure catalogue
+-- docs/                   # requirements, design, architecture, MCP manifest
+-- docs/week8/             # final report, evidence pack, deck, demo script
+-- release/                # changelog, release notes, tagging procedure
+-- demo/                   # demo launcher and presenter guide
+-- data/                   # synthetic corpus and fixtures
+-- requirements.txt
+-- .env.example
```

---

## Safety and data handling

- **No write without approval.** `create_draft_support_case` requires a host-injected approval flag;
  the model cannot set it.
- **No model-supplied identity.** The host injects the student ID after session validation.
- **Tool whitelist and typed arguments.** Unknown tools and malformed arguments are rejected before
  execution.
- **Bounded loop.** Iterations, tool calls, questions, repeats, retries, model calls and wall-clock
  time are capped in code.
- **Data minimisation.** Memory stores `active_case_id` and minimal metadata only, never the
  transcript. 30-day TTL; deletion on request; `memory_audit.jsonl` records events.
- **Synthetic corpus.** `data/` contains no real student records.

---

## Known limitations

1. **R14 lexical false positive.** Retrieval is 14/15; a lexically similar paragraph is cited instead
   of abstaining. A local coverage guard (`MIN_COVER=2`) reaches 15/15 on that set but is **not
   merged** into v1.0.0 because the 49-scenario evidence predates it.
2. **Live-model evidence gap.** The 49-scenario run uses a scripted planner. It proves the
   orchestration, tools and safety layers, not live Gemini action choice.
3. **Unverified failure history.** `FC-12` to `FC-14` have verified before/after evidence;
   `FC-01` to `FC-11` are documented but their pre-fix baseline was not preserved. See
   `evidence/week7_failures/CATALOGUE_EVIDENCE.md`.
4. **Synthetic corpus.** External validity for real policy edge cases is limited.
5. **Prototype operations.** No authentication, rate limiting or structured log shipping.
6. **No CI.** Harnesses are run manually.

---

## Release

- Version: **v1.0.0** (annotated tag prepared)
- Final documents: [`docs/week8/`](../docs/week8/)
- Changelog: [`release/CHANGELOG.md`](CHANGELOG.md)
- Release notes: [`release/RELEASE_NOTES_v1.0.0.md`](RELEASE_NOTES_v1.0.0.md)
- Tagging procedure: [`release/TAGGING.md`](TAGGING.md)

The remote tag and GitHub release are created by the maintainer with the procedure in
`release/TAGGING.md`; they are not created by this repository snapshot.

---

## Team

| Member | Student number |
|---|---|
| Namatovu Christine Maria | 2300701098 |
| Opiyo Oscar | 2300701330 |
| Isio Lily | 2300700445 |
| Babirye Sandra | 2300707270 |
| Ogwal Richard | 2300716574 |

Course: BSE4104 Emerging Trends in Software Engineering, Makerere University.
