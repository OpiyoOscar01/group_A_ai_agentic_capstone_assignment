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
