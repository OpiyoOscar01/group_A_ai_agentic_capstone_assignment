# University Student-Support Case Agent — Group A Day (BSE4104)

AI-native bounded agent: grounded handbook Q&A, timetable/case lookup, draft-only case creation with human approval.

## CampusIQ website (Flask + React)
CampusIQ is the browser interface for this student-support prototype. It connects to the existing Gemini-planned bounded agent, RAG knowledge collection, case and timetable tools, and student memory. The interface includes a guided assistant, saved chat history, handbook search, case list, timetable, search history, and a description of the system's boundaries.

The demo sign-in accepts **only a student ID from the synthetic sample roster**. It is not real authentication. The existing JSON files remain the source for student, case, and timetable records. SQLite stores handbook-search metadata and chat transcripts scoped to the selected demo student. Students can review and delete saved chats. The case-workflow planner uses Gemini to propose one allowed action at a time; the deterministic controller validates every proposal, and handbook Q&A continues to use the project's source-retrieval pipeline. Transcript history survives Flask restarts; an unfinished case approval does not, so after a restart the saved draft is for reference and a new request is needed to continue.

### Start locally
Use two terminals from the repository root:

**Terminal 1 — Flask API**
```powershell
python -m pip install -r requirements.txt
python src/webapp.py
```

**Terminal 2 — React development server**
```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://127.0.0.1:5173`) and select a demo student profile. The Vite server proxies API requests to Flask on port 5000.

To serve a production frontend through Flask:
```powershell
cd frontend
npm run build
cd ..
python src/webapp.py
```
Then open `http://127.0.0.1:5000`.

Create an untracked `.env` file and set `GEMINI_API_KEY` from Google AI Studio; the app uses the configured Gemini model (`GEMINI_MODEL`, default `gemini-3.8-flash`) as the bounded case-workflow planner. Without a key, ordinary retrieval and lookup questions still work, but case-agent planning reports that Gemini is unavailable rather than silently switching to the scripted planner. See `.env.example`. `CAMUS_SECRET_KEY` should be replaced with a private random value when using a stable local session. The default generated key is suitable only for a single local development process. **The demo sign-in is not authentication. Chat messages are sent to Gemini during case planning and stored locally until deleted. Use synthetic data only; never enter real or sensitive student information, and do not expose this prototype publicly.**

## Quickstart (Week 2 baseline)
```
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY (or run MOCK mode without key)
python src/app.py --run-tests
python src/app.py --chat
```

## Week 3 RAG
```
python src/rag.py --run-tests        # 14/15 pass
python src/rag.py --query "How many times can I retake a failed course?"
```

## Week 5 Bounded agent
```
python tests/run_week5_agent_traces.py     # 13 scenarios, writes evidence/week5_traces/
python src/agent.py --chat --student 2300701098                 # scripted planner
python src/agent.py --chat --student 2300701098 --planner gemini   # needs GEMINI_API_KEY
```
- `src/agent.py` controller + validation gate + planners; `docs/architecture/week5_agent_architecture.png`; contract in `docs/requirements/Week5/`

## Week 6 Memory, state and interfaces
```
python tests/run_week6_memory_demo.py     # 8 scenarios (M1-M7, I1), writes evidence/week6_memory/
```
- `src/memory.py` persistent memory (active case ID only); `docs/design/` state model, memory note, MCP-style spec; `docs/interfaces/support_case_mcp_manifest.json`

## Week 7 Evaluation, observability, guardrails
```
python tests/run_week7_eval.py --label final          # 49 scenarios, writes evidence/week7_eval/final/
python tests/retest_failures.py                       # Failure Catalogue before/after + re-tests
```
- `tests/week7_eval_set.json` dataset; `evidence/week7_eval/` contains the retained evaluation reports; `evidence/week7_failures/` contains catalogue evidence

## Structure
- `docs/requirements/` — charter, user stories, boundary matrix, model note, prompt specs
- `docs/weekly-reports/` — Week 1–3 progress reports
- `docs/evaluation/` — 10-case (W2) + 15-case (W3) evaluation
- `docs/architecture/` — RAG diagram
- `prompts/` — v1.0, v1.1, v2.0, v3.0-rag
- `knowledge/` — 12-doc synthetic corpus with provenance (no real student data)
- `src/` — app.py (W2), rag.py (W3), agent.py (bounded agent), webapp.py (Flask API)
- `frontend/` — React + Vite browser interface for CampusIQ
- `data/camus_iq.sqlite3` — local, ignored SQLite database for handbook search metadata and saved conversations
- `tests/` — eval case JSONs
- `evidence/traces/` — run traces

Repo: https://github.com/OpiyoOscar01/group_A_ai_agentic_capstone_assignment
