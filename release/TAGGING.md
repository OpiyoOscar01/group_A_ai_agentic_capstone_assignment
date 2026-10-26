# Release Tagging Procedure — v1.0.0

Run these steps from a clean checkout of `main`. The tag must point at the commit whose tree matches
the evidence index in `evidence/week8/FINAL_EVIDENCE_INDEX.md`.

## 1. Pre-flight checks

```bash
git status                     # must be clean
git branch --show-current      # must be main
git log --oneline -5
```

Confirm:

- [ ] The repository README is current, including `src/web_ui.py` and `tests/run_week7_eval.py`.
- [ ] `.gitignore` excludes `.env`, virtual environments and caches.
- [ ] No secret, key or local absolute path is committed:
      `git grep -n -I "GEMINI_API_KEY=\|C:\\\\Uni\|/Users/" -- ':!*.md'` returns nothing sensitive.
- [ ] `requirements.txt` is pinned and installs cleanly in a fresh environment.
- [ ] Evidence files referenced in the index exist in the tree.

## 2. Reproduce the headline results

```bash
python tests/run_week7_eval.py --label local
python tests/run_week7_guardrails.py
```

Expected: end-to-end 49/49 with zero safety violations; guardrails 16/16. Record the commit hash:

```bash
git rev-parse HEAD
```

Add the hash to the release notes and evidence index before tagging.

## 3. Create the annotated tag

```bash
git tag -a v1.0.0 -m "v1.0.0: final capstone release

- 49/49 end-to-end scenarios (TC/GR/TS/IF 100%)
- 16/16 guardrail probes, 0 safety violations
- 13/13 agent traces, 8/8 memory scenarios, 39/39 traceable runs
- scripted-planner p95 latency 32.6 ms (budget 2000 ms)
- honest evidence: R14 14/15; FC-01..FC-11 before/after unverified

See RELEASE_NOTES_v1.0.0.md."
```

## 4. Push the tag and publish

```bash
git push origin main
git push origin v1.0.0
```

Then create the GitHub release from tag `v1.0.0`, using `RELEASE_NOTES_v1.0.0.md` as the body, and
attach the Week 8 PDFs, the `.pptx` deck and the evidence pack.

## 5. Post-tag verification

```bash
git ls-remote --tags origin | grep v1.0.0
```

- [ ] Tag exists on the remote and points at the intended commit.
- [ ] Release page shows the notes and attachments.
- [ ] Fresh clone + `git checkout v1.0.0` + `pip install -r requirements.txt` succeeds.
- [ ] ClickUp release task is marked Done with the tag URL.

## 6. If a mistake is found after tagging

Do **not** move or force-push a published tag. Create a new patch release (`v1.0.1`) with the fix and a
changelog entry. This preserves the reproducibility of any evidence collected against `v1.0.0`.
