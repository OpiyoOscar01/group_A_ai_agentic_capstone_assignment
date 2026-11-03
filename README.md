# CampusIQ — University Student-Support Agent

Repository: <https://github.com/OpiyoOscar01/group_A_ai_agentic_capstone_assignment>
Clickup Link: <https://app.clickup.com/1200410000004185/v/o/s/1200410000006385>

CampusIQ is a student-support prototype developed for **BSE4104 Emerging Trends in Software
Engineering, Makerere University**. It combines grounded handbook Q&A, student-specific case and
timetable lookups, and a bounded workflow for preparing support cases.

> **Safety boundary:** AI can propose the next step, but deterministic application code validates
> proposals. A support case is created only after the student explicitly approves its draft.

## What CampusIQ does

- Answers questions using the approved local handbook collection and cites a source, or abstains when
  the collection does not support an answer.
- Shows the signed-in demo student's timetable and support cases.
- Collects required details for a support case, checks policy and existing cases, then presents a
  draft for review before submission.
- Saves handbook-search metadata and chat transcripts locally in SQLite.
- Applies limits and checks to planner actions, input, tool calls, and approval.

## Start the CampusIQ website

### Requirements

- Python and `pip`
- Node.js and npm
- A Gemini API key for Gemini-powered case-workflow planning

From the repository root, install the Python packages:

```powershell
python -m pip install -r requirements.txt
```

To enable Gemini case planning, set the API key in an untracked `.env` file. If you do not have one
yet:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env` and set `GEMINI_API_KEY`. The default model is `gemini-3.8-flash`; set `GEMINI_MODEL` to
override it. Never commit `.env`.

Start the app from the repository root:

```powershell
python src/webapp.py
```

The startup script installs the locked frontend dependencies if Vite is missing, builds the React
frontend, and starts Flask. Open **http://127.0.0.1:5000**. Press `Ctrl+C` to stop it. Node.js and npm
must be installed and available on `PATH`.

### Frontend development mode

For Vite hot reload, keep Flask running and use a second terminal:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Open the Vite URL (normally **http://127.0.0.1:5173**). Its `/api` requests are proxied to Flask on
port 5000. This second terminal is only needed for frontend development; the normal local app uses the
built frontend served by Flask.

## Gemini and scripted planning

The CampusIQ web app prefers the Gemini planner for support-case workflows. Gemini proposes one
bounded action at a time; application code validates and executes allowed actions. If a Gemini request
fails with a recognized service, quota, or access error, the scripted planner takes over. Automatic
Gemini retries are disabled and planner requests have a 15-second timeout to avoid lengthy waits before
fallback.

The direct agent CLI uses gemini planner by default. Choose the planner explicitly with
`--planner gemini` or `--planner scripted`.

**Handbook answers do not use Gemini.** They use the local TF-IDF retrieval pipeline and answer from
approved documents. Case planning is separate from handbook Q&A.

## Sign-in, storage, and privacy

Choose a student ID from the app's synthetic demo roster. This is a profile selector, **not real
authentication**. Student, case, and timetable fixtures are loaded from JSON files in `data/`.
Handbook-search metadata and conversation transcripts are stored locally in
`data/camus_iq.sqlite3`; students can delete saved conversations. In-progress approval state exists
only while the Flask process is running. After a restart, start a new case request rather than trying
to approve a saved draft.

Use synthetic data only. Do not enter real, sensitive, or confidential student information, and do not
expose this prototype publicly. During Gemini-powered case planning, message content is sent to the
configured Gemini service.

## Project work by week

| Week        | Focus                          | Project outcome                                                                                                     |
| ----------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| 1           | Project definition             | Charter, requirements, user needs, and initial design artifacts.                                                    |
| 2           | Prompt-engineering baseline    | Command-line student-support agent, model-selection notes, prompt specifications, and baseline scenarios.           |
| 3           | Retrieval-augmented generation | Synthetic handbook corpus, TF-IDF retrieval, cited answers, abstention behavior, and retrieval evaluation.          |
| 4           | Tools and orchestration        | Typed lookup and draft-case tools, routing, tool schemas, and tool tests.                                           |
| 5           | Bounded agent                  | Plan–validate–act workflow, scripted and Gemini planners, explicit approval, limits, and workflow traces.           |
| 6           | Memory and state               | Minimal active-case memory, state handling, expiry and deletion behavior, and interface documentation.              |
| 7           | Evaluation and guardrails      | End-to-end evaluation, failure retests, guardrail checks, tracing, and retained evidence.                           |
| Integration | CampusIQ interface             | Flask API and React website bring the handbook, timetable, case workflow, saved chats, and search history together. |

Weekly reports are in `docs/weekly-reports/`. Requirements, evaluation reports, design notes, and
architecture materials are in `docs/`.

## Developer command-line tools

The supported browser app is **CampusIQ**, started with `python src/webapp.py` above. The following
commands are separate project exercises and do not start the CampusIQ website:

Run these from the repository root:

```powershell
# Week 2 baseline
python src/app.py --chat
python src/app.py --run-tests

# Handbook retrieval
python src/rag.py --query "How many times can I retake a failed course?"
python src/rag.py --run-tests

# Bounded case agent (scripted planner by default)
python src/agent.py --chat --student 2300701098
python src/agent.py --chat --student 2300701098 --planner gemini
```

## Tests and evaluation

Run the CampusIQ API tests:

```powershell
python -m unittest discover -s tests -p test_webapp.py
```

Additional project test and evaluation runners:

```powershell
python tests/run_week4_tool_tests.py
python tests/run_week5_agent_traces.py
python tests/run_week6_memory_demo.py
python tests/run_week7_eval.py --label final
python tests/run_week7_guardrails.py
python tests/retest_failures.py
```

Evaluation scripts may write traces or reports under `evidence/`. Retained results describe the
specific runs that produced them; they are not a guarantee of current Gemini service availability.

## Repository map

| Location        | Contents                                                                     |
| --------------- | ---------------------------------------------------------------------------- |
| `src/webapp.py` | Flask API, database initialization, and frontend build/serving               |
| `src/agent.py`  | Bounded agent, planners, validation, and support-case workflow               |
| `src/rag.py`    | Local corpus loading, TF-IDF retrieval, and grounded answers                 |
| `src/tools.py`  | Case, timetable, and support-case tools                                      |
| `src/memory.py` | Active-case memory and audit handling                                        |
| `frontend/`     | React + Vite CampusIQ website                                                |
| `knowledge/`    | Approved synthetic support documents                                         |
| `data/`         | Synthetic demo fixtures and local application data                           |
| `tests/`        | Unit tests, scenario sets, and evaluation runners                            |
| `evidence/`     | Evaluation results, traces, and project evidence                             |
| `docs/`         | Weekly reports, requirements, design, evaluation, and architecture documents |
| `prompts/`      | Versioned prompts from the project exercises                                 |

Repository: <https://github.com/OpiyoOscar01/group_A_ai_agentic_capstone_assignment>
Clickup Link: <https://app.clickup.com/1200410000004185/v/o/s/1200410000006385>
