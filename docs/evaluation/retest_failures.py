"""
Week 7 - Failure Catalogue evidence generator.
Joins each catalogued failure to (a) the BASELINE result (Week 6 code) and (b) the FINAL result (fixed code),
and re-tests the three earlier failures (FC-12..14) by reproducing them with the fix disabled.

Run (after both evaluation runs exist):  python evaluation/retest_failures.py
Output: evidence/week7_failures/catalogue_evidence.json and .md
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src")); sys.path.insert(0, str(BASE / "evaluation")); sys.path.insert(0, str(BASE / "tests"))
OUT = BASE / "evidence" / "week7_failures"; OUT.mkdir(parents=True, exist_ok=True)

def load(label):
    d = json.loads((BASE / "evidence" / "week7_eval" / label / "results.json").read_text())
    return {r["id"]: r for r in d["results"]}, d["summary"]

base, bsum = load("baseline"); final, fsum = load("final")
NEW = [  # id, title, scenarios that exposed it
    ("FC-01", "Unregistered student ID could create a support case (authorization gap)", ["U05", "U10"]),
    ("FC-02", "Non-case replies exposed the raw internal RAG trace (model, prompt version, chunk IDs, excerpts)", ["N06", "E09", "A04", "A07", "U03"]),
    ("FC-03", "Answers in natural wording not understood: redundant questions and NEEDS_INFO", ["E01", "E03", "E04"]),
    ("FC-04", "Stated academic year ignored; 2026 silently assumed in the draft", ["E02"]),
    ("FC-05", "Natural approval wording ('Yes, please submit it') treated as a decline", ["E05"]),
    ("FC-06", "Duplicate rule ignored the semester: a legitimate new case was blocked", ["E07"]),
    ("FC-07", "Boundary check refused a request that merely mentioned a fee", ["E08"]),
    ("FC-08", "Boundary replies cited the wrong policy notices", ["U06", "U07", "U08", "U09"]),
    ("FC-09", "No input bound: a 5,000-character message was processed whole", ["E10"]),
    ("FC-10", "Injection phrasing not recognised ('disregard your instructions ... without asking me')", ["A02"]),
]
rows = []
for fid, title, ids in NEW:
    rows.append({"id": fid, "title": title, "scenarios": ids,
                 "before": {i: ("PASS" if base[i]["passed"] else "FAIL: " + "; ".join(base[i]["failures"] + ["SAFETY: " + v for v in base[i]["violations"]])[:230]) for i in ids},
                 "after": {i: "PASS" if final[i]["passed"] else "FAIL" for i in ids},
                 "retested_ok": all(final[i]["passed"] for i in ids) and not all(base[i]["passed"] for i in ids)})
btr, ftr = bsum["traceability"], fsum["traceability"]
rows.append({"id": "FC-11", "title": "Traces lacked latency, model/prompt version and retrieval evidence", "scenarios": ["all runs"],
             "before": {"traceability": f"{btr[0]}/{btr[1]} traces complete"}, "after": {"traceability": f"{ftr[0]}/{ftr[1]} traces complete"},
             "retested_ok": btr[0] == 0 and ftr[0] == ftr[1]})

# ---- FC-12: retrieval near-miss (Week 5): disable the stricter bar and re-run F05
import tools, agent as A
from run_week7_eval import run_one
spec = next(s for s in json.loads((BASE / "evaluation" / "week7_eval_set.json").read_text())["scenarios"] if s["id"] == "F05")
keep = A.OTHER_MIN_SCORE
A.OTHER_MIN_SCORE = 0.0
b, _ = run_one(spec); A.OTHER_MIN_SCORE = keep
a, _ = run_one(spec)
rows.append({"id": "FC-12", "title": "Retrieval near-miss: unrelated 'parking permit' request retrieved DOC-02 at 0.168, just above the 0.14 bar (found Week 5)",
             "scenarios": ["F05"], "before": {"F05 with fix disabled": f"stop={b['stop']}, new cases={b['new_cases']} (a draft would be shown)"},
             "after": {"F05": f"stop={a['stop']}"}, "retested_ok": a["stop"] == "NO_SOURCE" and b["stop"] != "NO_SOURCE"})

# ---- FC-13: Week 4 runner wrote to the real data file (found Week 6): original vs fixed, in throwaway copies
def case_count(root): return len(json.loads((Path(root) / "data" / "cases.json").read_text()))
def run_in_copy(runner_src):
    tmp = Path(tempfile.mkdtemp(prefix="fc13_"))
    for d in ("src", "data", "tests", "knowledge"): shutil.copytree(BASE / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__"))
    (tmp / "evidence" / "week4_traces").mkdir(parents=True)
    if runner_src: shutil.copy(runner_src, tmp / "tests" / "run_week4_tool_tests.py")
    n0 = case_count(tmp)
    subprocess.run([sys.executable, str(tmp / "tests" / "run_week4_tool_tests.py")], capture_output=True, cwd=tmp)
    n1 = case_count(tmp); shutil.rmtree(tmp, ignore_errors=True); return n0, n1
o0, o1 = run_in_copy(BASE / "evaluation" / "legacy" / "run_week4_tool_tests_original.py")
f0, f1 = run_in_copy(None)
rows.append({"id": "FC-13", "title": "Week 4 test runner wrote a new case into the real data/cases.json on every run (found Weeks 5-6)",
             "scenarios": ["Week 4 suite"], "before": {"original runner": f"cases {o0} -> {o1}"}, "after": {"fixed runner": f"cases {f0} -> {f1}"},
             "retested_ok": o1 > o0 and f1 == f0})

# ---- FC-14: Week 6 test hard-coded CASE-0005 (found Week 6): pollute data, re-run Week 6 suite
tmp = Path(tempfile.mkdtemp(prefix="fc14_"))
for d in ("src", "data", "tests", "knowledge", "docs"): shutil.copytree(BASE / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__"))
cs = json.loads((tmp / "data" / "cases.json").read_text())
cs.append({**cs[-1], "case_id": f"CASE-{len(cs)+1:04d}", "student_id": "2300716574", "name": "Ogwal Richard", "description": "polluting case"})
(tmp / "data" / "cases.json").write_text(json.dumps(cs))
p = subprocess.run([sys.executable, str(tmp / "tests" / "run_week6_memory_demo.py")], capture_output=True, text=True, cwd=tmp)
ok14 = "8/8 scenarios pass" in p.stdout; shutil.rmtree(tmp, ignore_errors=True)
rows.append({"id": "FC-14", "title": "Week 6 test hard-coded the new case ID (CASE-0005) and failed when earlier tests had added a case (found Week 6)",
             "scenarios": ["Week 6 suite"], "before": {"observed Week 6": "AssertionError 'seed failed' after Week 4 test added a case"},
             "after": {"Week 6 suite on polluted data": "8/8 scenarios pass" if ok14 else "FAIL"}, "retested_ok": ok14})

(OUT / "catalogue_evidence.json").write_text(json.dumps({"baseline": bsum, "final": fsum, "failures": rows}, indent=1))
md = ["# Failure Catalogue evidence (generated)\n", f"Baseline: {bsum['passed']}/{bsum['scenarios']} pass, {bsum['safety_violations']} safety violations. "
      f"Final: {fsum['passed']}/{fsum['scenarios']} pass, {fsum['safety_violations']} safety violations.\n", "| ID | Failure | Before | After | Re-test |", "|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['id']} | {r['title']} | {'; '.join(f'{k}: {v}' for k, v in r['before'].items())[:200]} | {'; '.join(f'{k}: {v}' for k, v in r['after'].items())[:120]} | {'PASS' if r['retested_ok'] else 'FAIL'} |")
(OUT / "CATALOGUE_EVIDENCE.md").write_text("\n".join(md).replace("\n\n|", "\n|") + "\n", encoding="utf-8")
for r in rows: print(r["id"], "re-test", "PASS" if r["retested_ok"] else "FAIL", "|", list(r["after"].values())[:2])
print("all re-tests pass:", all(r["retested_ok"] for r in rows))
