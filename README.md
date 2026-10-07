# University Student-Support Case Agent — Group A Day (BSE4104)

AI-native bounded agent: grounded handbook Q&A, timetable/case lookup, draft-only case creation with human approval.

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

## Structure
- `docs/requirements/` — charter, user stories, boundary matrix, model note, prompt specs
- `docs/weekly-reports/` — Week 1–3 progress reports
- `docs/evaluation/` — 10-case (W2) + 15-case (W3) evaluation
- `docs/architecture/` — RAG diagram
- `prompts/` — v1.0, v1.1, v2.0, v3.0-rag
- `knowledge/` — 12-doc synthetic corpus with provenance (no real student data)
- `src/` — app.py (W2) + rag.py (W3)
- `tests/` — eval case JSONs
- `evidence/traces/` — run traces

Repo: https://github.com/OpiyoOscar01/group_A_ai_agentic_capstone_assignment
