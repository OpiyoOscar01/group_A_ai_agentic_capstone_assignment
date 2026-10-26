# Final Evidence Index — v1.0.0

Every claim in the Final Engineering Report and Release Notes links to a retained artefact below.
Paths are relative to the repository root unless marked **[local]** (submitted alongside the Week 8
package). Verification status is stated explicitly; "unverified" is a deliberate label, not an omission.

## 1. Headline claims

| Claim | Value | Evidence | Status |
|---|---|---|---|
| End-to-end scenarios passed | 49/49 (100%) | `evidence/week7_eval/final/RESULTS.md` | Verified |
| Task completion (TC) | 100% | `evidence/week7_eval/final/results.json` | Verified |
| Goal recognition (GR) | 100% | `evidence/week7_eval/final/results.json` | Verified |
| Tool selection (TS) | 100% | `evidence/week7_eval/final/results.json` | Verified |
| Information faithfulness (IF) | 100% | `evidence/week7_eval/final/results.json` | Verified |
| Safety violations | 0 | runner output + traces | Verified |
| Traceability | 39/39 run records | `evidence/week7_eval/final/` | Verified |
| Latency p50 / p95 / max | 1.9 / 32.6 / 57.0 ms | `evidence/week7_eval/final/results.json` | Verified (scripted) |
| Guardrail probes | 16/16 | `evidence/week7_guardrails/SUMMARY.md` | Verified |
| Memory scenarios | 8/8 | `evidence/week6_memory/SUMMARY.md` | Verified |
| Agent workflow traces | 13/13 | `evidence/week5_traces/SUMMARY.md` | Verified |
| Retrieval cases | 14/15 (93%) | Week 3 deliverable and trace | Verified |
| Traceability matrix | 39/39 links | Week 7 matrix | Verified |

## 2. Failure catalogue

| Finding | Status | Evidence | Note |
|---|---|---|---|
| FC-12 parking-permit boundary misroute | Verified | `evidence/week7_failures/catalogue_evidence.json` | Before/after preserved |
| FC-13 repeated-action stall | Verified | `evidence/week7_failures/catalogue_evidence.json` | Before/after preserved |
| FC-14 case-status ownership leak | Verified | `evidence/week7_failures/catalogue_evidence.json` | Before/after preserved |
| FC-01 to FC-11 | **Not verified** | `evidence/week7_failures/CATALOGUE_EVIDENCE.md` | Pre-fix revision not preserved; "baseline" is an output folder |

The prose Failure Catalogue describes a 29/49 → 49/49 improvement with fourteen re-tests passing. That
narrative is **not** supported by the retained evidence for FC-01..FC-11 and is superseded by
`CATALOGUE_EVIDENCE.md`. The Week 7 Progress Report flags the same inconsistency.

## 3. Known gaps

| Gap | Consequence | Next action |
|---|---|---|
| R14 lexical false positive | One confident wrong citation in the 15-case retrieval set | Merge coverage guard after a full regression |
| Scripted-planner evaluation | Live Gemini action choice not benchmarked | Run live planner end to end; retain traces |
| Unverified FC-01..FC-11 | Causal "fixed" claims unsupported | Preserve pre-fix revisions; re-run baseline |
| DOC-12 v1.1 not re-evaluated | Retrieval result predates corpus change | Re-run Week 3 set; add held-out cases |
| No CI | Manual regression risk | Add CI for both harnesses |
| No auth / rate limiting | Not deployment-ready | Add before any pilot |

## 4. Scenario and trace artefacts

| Artefact | Path |
|---|---|
| 49 scenario definitions | `tests/week7_eval_set.json` |
| End-to-end harness | `tests/run_week7_eval.py` |
| Guardrail harness | `tests/run_week7_guardrails.py` |
| Agent trace harness | `tests/run_week5_agent_traces.py` |
| Memory harness | `tests/run_week6_memory_demo.py` |
| Tool test data | `tests/week4_tool_tests.json` |
| MCP-style manifest | `docs/interfaces/support_case_mcp_manifest.json` |

## 5. Design and governance artefacts

| Artefact | Path |
|---|---|
| Requirements and boundary matrix | Week 1 deliverable |
| Model selection and prompt spec | Week 2 deliverable; `prompts/` |
| Retrieval design and evaluation | Week 3 deliverable |
| Tool contracts and integration | Week 4 deliverable; `tools_schemas/` |
| Agent task contract and limits | Week 5 deliverable; `src/agent.py` |
| Memory and state model | Week 6 deliverable; `src/memory.py` |
| Architecture diagrams | `docs/architecture/` |
| Traceability matrix | Week 7 deliverable (39/39) |

## 6. Week 8 package (**[local]**)

| Deliverable | Path |
|---|---|
| Final engineering report | `docs/week8/Week8_01_Final_Engineering_Report.pdf` / `.docx` |
| Final evaluation and evidence pack | `docs/week8/Week8_02_Final_Evaluation_Evidence_Pack.pdf` / `.docx` |
| Presentation deck | `docs/week8/Week8_03_Final_Presentation.pptx` |
| Demonstration script | `docs/week8/Week8_04_Demo_Script.pdf` / `.docx` |
| Results chart | `docs/week8/week8_results_chart.png` |
| Release README, changelog, notes, tagging | `release/` |
| This index | `evidence/week8/FINAL_EVIDENCE_INDEX.md` |
| ClickUp board and contributions | `evidence/week8/Week8_ClickUp_Board_and_Contribution.md` |

## 7. Reproduction commands

```bash
pip install -r requirements.txt
python tests/run_week7_eval.py --label local
python tests/run_week7_guardrails.py
python tests/run_week5_agent_traces.py
python tests/run_week6_memory_demo.py
python src/web_ui.py
```

The end-to-end and guardrail harnesses use the scripted planner and need no network access. A live-model
smoke test requires `GEMINI_API_KEY`.

## 8. Sign-off

| Check | Owner | Status |
|---|---|---|
| Evidence paths exist in tagged tree | Release lead | To confirm at tag time |
| Results reproduce | Evaluation lead | To confirm at tag time |
| No secrets committed | Release lead | To confirm at tag time |
| Report figures match evidence | Project lead | To confirm before submission |
| ClickUp board updated | Documentation lead | To confirm before submission |

*Prepared for Week 8. Sign-off is completed by the team at release time; this index is the checklist.*
