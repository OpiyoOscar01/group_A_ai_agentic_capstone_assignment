# Release Notes — v1.0.0

**Release date:** 23 October 2026
**Project:** University Student-Support Case Agent
**Course:** BSE4104 Emerging Trends in Software Engineering, Makerere University
**Team:** Group A Day

---

## Summary

v1.0.0 is the final capstone release: a bounded agentic assistant for routine university student
support. It answers policy questions with citations, looks up case and timetable records through typed
tools, and creates a `Pending` support case only after explicit student approval. Every loop is
bounded, every run is traced, and the human-approval boundary is enforced in code rather than in the
prompt.

## What is included

| Deliverable | Location |
|---|---|
| Final engineering report (PDF + DOCX) | `docs/week8/Week8_01_Final_Engineering_Report.*` |
| Final evaluation and evidence pack | `docs/week8/Week8_02_Final_Evaluation_Evidence_Pack.*` |
| Presentation deck | `docs/week8/Week8_03_Final_Presentation.pptx` |
| Demonstration script | `docs/week8/Week8_04_Demo_Script.*` |
| Corrected repository README | `release/README_FINAL.md` |
| Evidence index | `evidence/week8/FINAL_EVIDENCE_INDEX.md` |
| ClickUp board and contribution record | `evidence/week8/Week8_ClickUp_Board_and_Contribution.md` |
| Architecture diagrams | `diagrams/` |

## Verified results

| Criterion | Result |
|---|---|
| End-to-end scenarios | **49/49 (100%)** |
| Task completion / goal recognition / tool selection / information faithfulness | **100% each** |
| Safety violations | **0** |
| Guardrail probes | **16/16** |
| Memory scenarios | **8/8** |
| Agent workflow traces | **13/13** |
| Traceability | **39/39 run records** |
| Latency (scripted planner) | **p50 1.9 ms · p95 32.6 ms · max 57.0 ms** |
| Retrieval (Week 3 set) | **14/15 (93%)** |

## What is deliberately not included

1. **The coverage-guard retrieval fix.** A minimum-coverage guard (`MIN_COVER=2`) passes 15/15 on the
   Week 3 set, but merging it after the 49-scenario evidence was produced would make that evidence
   unreproducible. It stays out of v1.0.0 and is the first item for the next release.
2. **Verified before/after history for FC-01 to FC-11.** Only `FC-12`–`FC-14` have preserved
   before/after evidence. The catalogue's early "baseline" is an output folder, not a pre-fix revision,
   so those eleven findings are reported as documented-but-unverified.
3. **A live-model benchmark.** The 49-scenario run uses a scripted planner for determinism. It proves
   the orchestration, validation, tool and safety layers; it does not prove live Gemini action choice.

These exclusions are stated in the report and evidence pack, not hidden.

## Upgrade / run instructions

```bash
git fetch --tags
git checkout v1.0.0          # if the tag has been pushed
pip install -r requirements.txt
python src/web_ui.py          # scripted mode, no key required
# optional live planner:
cp .env.example .env          # add GEMINI_API_KEY
python src/web_ui.py --planner gemini
```

Prerequisite: Python 3.11+. Scripted mode needs no API key; the optional live planner needs one.
No real student data is used; the corpus is synthetic.

## Breaking changes

This is the first stable release, so there is no migration path. The pre-release README referenced
`evaluation/run_week7_eval.py`; the harness is under `tests/`. Use the corrected paths in the repository README or `release/README_FINAL.md`.

## Reproduction

```bash
python tests/run_week7_eval.py --label local
python tests/run_week7_guardrails.py
python tests/run_week5_agent_traces.py
python tests/run_week6_memory_demo.py
```

The first two commands reproduce the headline results without network access.

## Acknowledgements

Gemini 2.0 Flash (Google) for the application model; the course team for the weekly review structure;
and the open-source Python, python-docx and python-pptx communities.

## Known issues

- R14 retrieval false positive (14/15).
- Prototype lacks authentication, rate limiting and CI.
- DOC-12 v1.1 has not been followed by a retrieval re-run.

## Contact

Repository: <https://github.com/OpiyoOscar01/group_A_ai_agentic_capstone_assignment>
