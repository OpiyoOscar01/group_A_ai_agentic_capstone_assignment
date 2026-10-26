# Week 8 ClickUp Board and Contribution Record

This file is the source for the Week 8 ClickUp board and the individual-contribution evidence required
by the assignment. It lists the board structure, the Week 8 tasks with owners and acceptance criteria,
the weekly contribution matrix, and the review/release sign-off checklist. Statuses marked **Prepared**
mean the artefact exists in this package; **To verify** means the team must execute and confirm it in
the repository or ClickUp before submission.

## 1. Board structure

Space: **BSE4104 Capstone — Group A Day**

| List | Purpose |
|---|---|
| Backlog | Ideas and deferred work (post-v1.0.0) |
| This week (Week 8) | Hardening, release, report, deck, demo |
| In review | Work awaiting a second team member |
| Done | Completed with evidence link |
| Blocked | Work waiting on access or a dependency |

Every task uses the fields: **Owner**, **Week**, **Deliverable**, **Evidence link**, **Due date**. Every
"Done" task must contain a link to a file, commit, tag or recording — not only a comment.

## 2. Week 8 task board

| # | Task | Owner | Acceptance criterion | Evidence | Status |
|---|---|---|---|---|---|
| W8-01 | Freeze release scope and confirm what is in/out | Ogwal Richard | In/out list agreed; exclusions documented | `RELEASE_NOTES_v1.0.0.md` | Prepared |
| W8-02 | Harden retrieval/agent code; confirm no regressions | Opiyo Oscar | Full 49-scenario run reproduces 49/49 | `evidence/week7_eval/final/` | To verify |
| W8-03 | Write final engineering report (10 sections) | Namatovu Christine Maria | 8–12 page body; figures match evidence | `docs/week8/Week8_01_*` | Prepared |
| W8-04 | Compile final evaluation and evidence pack | Isio Lily | Every claim maps to an artefact; gaps stated | `docs/week8/Week8_02_*`, `evidence/week8/FINAL_EVIDENCE_INDEX.md` | Prepared |
| W8-05 | Reconcile failure catalogue statuses | Babirye Sandra | Verified vs unverified split matches `CATALOGUE_EVIDENCE.md` | `evidence/week7_failures/` | Prepared |
| W8-06 | Build presentation deck (16 slides) | Babirye Sandra | Covers problem, architecture, eval, failure, demo | `docs/week8/Week8_03_*` | Prepared |
| W8-07 | Write and rehearse demonstration script | Isio Lily | 12–15 min; happy path, failure, guardrails | `docs/week8/Week8_04_*` | Prepared |
| W8-08 | Correct README and run instructions | Ogwal Richard | `tests/run_week7_eval.py` path; no secrets | `release/README_FINAL.md` | Prepared |
| W8-09 | Changelog and release notes | Ogwal Richard | Matches version history; known issues stated | `release/CHANGELOG.md`, `RELEASE_NOTES_v1.0.0.md` | Prepared |
| W8-10 | Tag and publish v1.0.0 | Ogwal Richard | Annotated tag on intended commit; release page live | GitHub release URL | To verify |
| W8-11 | Add diagrams and results chart to package | Opiyo Oscar | Images render in deck and report | `diagrams/`, `docs/week8/week8_results_chart.png` | Prepared |
| W8-12 | Update ClickUp and contribution record | Babirye Sandra | All tasks have evidence links | This file | To verify |
| W8-13 | Rehearse live demo (two dry runs) | All | Complete run under 15 min; fallback tested | Recording link | To verify |
| W8-14 | Final submission pack and sign-off | Namatovu Christine Maria | Checklist complete; PDFs open | Submission folder | To verify |

## 3. Weekly contribution matrix

Roles follow the artefacts each member authored across the repository. "Lead" indicates primary
authorship; "support" indicates review or contributing sections.

| Member | Week 1 | Week 2 | Week 3 | Week 4 | Week 5 | Week 6 | Week 7 | Week 8 |
|---|---|---|---|---|---|---|---|---|
| Namatovu Christine Maria | Lead: problem, requirements, boundary matrix | Support: model criteria | Support: corpus provenance | Support: integration review | Lead: agent task contract and goal | Support: state requirements | Lead: evaluation run, failure catalogue, progress report | Lead: final report, sign-off |
| Opiyo Oscar | Support: requirements | Lead: model selection and prompts | Lead: ingestion, chunking, retrieval | Lead: tools and integration | Lead: bounded agent implementation | Lead: memory implementation | Lead: guardrail and validation fixes | Lead: code hardening, diagrams, chart |
| Isio Lily | Support: user research | Support: prompt tests | Lead: retrieval evaluation design | Support: tool tests | Lead: workflow traces | Lead: memory scenarios | Lead: evaluation criteria and scenario design | Lead: evidence pack, demo script, rehearsal |
| Babirye Sandra | Support: problem framing | Support: model comparison | Support: failure analysis | Support: review | Support: trace review | Support: memory review | Lead: guardrail evidence, review, progress report | Lead: failure reconciliation, deck, ClickUp |
| Ogwal Richard | Support: governance | Support: prompt review | Support: architecture | Lead: orchestrator, approval gate, architecture | Lead: agent architecture and safety controls | Lead: MCP-style contract | Lead: observability and tracing | Lead: release, README, tagging |

## 4. Review log (to complete at each review)

| Date | Review | Attendees | Decisions | Actions |
|---|---|---|---|---|
| Week 8, day 1 | Scope freeze | All | Confirm v1.0.0 contents and exclusions | W8-01 |
| Week 8, day 3 | Evidence review | Isio Lily, Babirye Sandra, Namatovu C. M. | Accept verified/unverified split | W8-04, W8-05 |
| Week 8, day 4 | Release review | Ogwal Richard, Opiyo Oscar | README and tag content approved | W8-08, W8-10 |
| Week 8, day 5 | Demo rehearsal | All | Timing under 15 min; fallback works | W8-13 |

## 5. Release sign-off checklist

- [ ] Scope freeze recorded (W8-01).
- [ ] 49/49 and 16/16 reproduced on the release commit (W8-02, W8-10).
- [ ] Report body 8–12 pages; every figure traceable (W8-03).
- [ ] Evidence index paths all resolve in the tagged tree (W8-04).
- [ ] Failure catalogue statuses match retained evidence (W8-05).
- [ ] Deck and demo script reviewed by a second member (W8-06, W8-07).
- [ ] README paths corrected; no secrets committed (W8-08).
- [ ] Annotated tag `v1.0.0` pushed; GitHub release published (W8-10).
- [ ] Two full demo rehearsals completed (W8-13).
- [ ] Final pack submitted and signed off (W8-14).

## 6. Links to record

| Item | Link |
|---|---|
| Repository | https://github.com/OpiyoOscar01/group_A_ai_agentic_capstone_assignment |
| Release tag | `<add v1.0.0 tag URL after tagging>` |
| ClickUp space | `<add space URL>` |
| Demo recording | `<add recording URL>` |
| Presentation date | 27 / 29 / 30 October 2026 |
