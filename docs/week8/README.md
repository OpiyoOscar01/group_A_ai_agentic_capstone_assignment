# Week 8 Final Deliverables

Final package for Group A Day, BSE4104 AI Agentic Capstone.

| File | Purpose |
|---|---|
| `Week8_01_Final_Engineering_Report.pdf` / `.docx` | Final engineering report, 17 pages including appendices; sections 1-10 and references occupy 12 pages |
| `Week8_02_Final_Evaluation_Evidence_Pack.pdf` / `.docx` | Evidence pack: results, traceability, latency, guardrails, failure catalogue |
| `Week8_03_Final_Presentation.pptx` | Presentation deck for 27, 29 and 30 October 2026 |
| `Week8_04_Demo_Script.pdf` / `.docx` | 12-15 minute demonstration runbook and Q&A preparation |
| `week8_results_chart.png` | Results chart used in the report and deck |

## Verified headline results

- End-to-end: 49/49 (TC, GR, TS, IF all 100%)
- Safety violations: 0
- Guardrails: 16/16
- Memory: 8/8
- Agent traces: 13/13
- Traceability: 39/39
- Latency: p50 1.9 ms, p95 32.6 ms, max 57.0 ms (scripted planner, budget 2,000 ms)
- Retrieval: 14/15 (R14 lexical false positive retained as evidence)

The 49-scenario run uses the scripted planner. Live Gemini action choice is not benchmarked in the
retained evidence.

## Related repository paths

- `evidence/week8/FINAL_EVIDENCE_INDEX.md` - claim-to-artefact index
- `release/` - changelog, release notes and tagging procedure
- `demo/` - launcher and presenter guide
- `src/web_ui.py` - dependency-free demonstration interface
