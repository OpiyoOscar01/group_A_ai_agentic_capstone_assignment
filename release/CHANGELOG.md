# Changelog

All notable changes to the University Student-Support Case Agent. Versions follow the weekly
capstone increments; `v1.0.0` is the final release.

## [Unreleased]

### Added
- Coverage guard (`MIN_COVER=2`) for retrieval, verified 15/15 on the Week 3 set. **Not merged** —
  requires a full 49-scenario regression first.

### Planned
- Live Gemini planner end-to-end run with retained traces.
- Pre-fix revision per failure-catalogue entry, enabling reproducible before/after evidence.
- CI workflow for the end-to-end and guardrail harnesses.
- Authentication, rate limiting and structured logging.

## [1.0.0] - 2026-10-23

### Added
- Final engineering report, evaluation evidence pack, presentation deck and demonstration script.
- Reproducible release package and documented tagging procedure.
- Evidence index linking every report claim to a retained artefact.

### Changed
- README corrected: browser UI is `src/web_ui.py`; harness path is `tests/run_week7_eval.py`.
- Demonstration UI restyled with the Custosell design system (blue-600 primary, gray-50 canvas, white cards).
- Release notes distinguish verified from unverified failure-catalogue findings.

### Verified
- 49/49 end-to-end scenarios; TC/GR/TS/IF all 100%.
- 16/16 guardrail probes; zero safety violations.
- 8/8 memory scenarios; 13/13 agent traces; 39/39 traceable runs.
- p95 latency 32.6 ms (scripted planner).

### Known issues
- R14 retrieval false positive (14/15).
- FC-01 to FC-11 before/after history not reproducible.
- Live-model behaviour not benchmarked in retained evidence.

## [0.7.0] - Week 7

### Added
- 49-scenario evaluation harness (`tests/run_week7_eval.py`, `tests/week7_eval_set.json`).
- 16-probe guardrail harness (`tests/run_week7_guardrails.py`).
- Failure catalogue and evidence caveat (`evidence/week7_failures/`).
- Observability fields and traceability matrix.

### Fixed
- FC-12 parking-permit boundary misroute.
- FC-13 repeated-action stall.
- FC-14 case-status ownership leak.

## [0.6.0] - Week 6

### Added
- Minimal memory layer: `active_case_id`, 30-day TTL, revalidation, deletion, audit log.
- MCP-style tool manifest (`docs/interfaces/support_case_mcp_manifest.json`).
- State model diagram and 8 memory scenarios (8/8).

## [0.5.0] - Week 5

### Added
- Bounded agent loop with validation gate and enumerated stop conditions.
- Code-enforced limits (iterations, tool calls, questions, repeats, retries, model calls, seconds).
- 13 workflow traces (13/13).

## [0.4.0] - Week 4

### Added
- Two typed read tools and one guarded write tool.
- Orchestrator routing and human approval gate.
- Tool argument validation and ownership checks.

## [0.3.0] - Week 3

### Added
- Twelve-document synthetic corpus with provenance.
- Ingestion, 180/30-word chunking, TF-IDF indexing, cosine retrieval, top-3, min score 0.14.
- Citation, partial-answer and abstention policy.
- 15-case retrieval evaluation: 14/15 (R14 lexical false positive).

## [0.2.0] - Week 2

### Added
- Gemini 2.0 Flash integration and versioned system prompts (v1.0).
- Model-selection comparison and prompt specification.
- Baseline: mock planner 10/10 valid; live 8/10 valid + 2 partial.

## [0.1.0] - Week 1

### Added
- Problem statement, twelve user stories and acceptance criteria.
- AI boundary matrix and success measures.
- Traceability identifiers (US-n).
