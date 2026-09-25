"""Week 4 tool + guardrail test runner. Saves traces for Christine's report."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))
from guardrails import guarded_call
from tools import call_tool

TESTS = json.loads((BASE / "tests" / "week4_tools_tests.json").read_text())
TRACE_DIR = BASE / "evidence" / "traces"


def run_one(case: dict) -> tuple[bool, dict]:
    session = dict(case.get("session", {}))
    args = dict(case.get("args", {}))
    setup = case.get("setup")
    # unknown_student: use a valid-format ID with no record
    if setup == "unknown_student":
        args["student_id"] = "2400999999"
        session["student_id"] = "2400999999"
    # missing_store: point at a nonexistent file temporarily
    if setup == "missing_store":
        import tools as T
        real = T.TIMETABLE_FILE
        T.TIMETABLE_FILE = BASE / "data" / "timetable.MISSING.json"
        try:
            res = guarded_call(case["tool"], args, session)
        finally:
            T.TIMETABLE_FILE = real
        ok = res.get("error") == case["expect_error"]
        return ok, res
    res = guarded_call(case["tool"], args, session)
    blob = json.dumps(res)
    ok_err = (res.get("error") == case["expect_error"]
              or (case["expect_error"] is None and "error" not in res))
    ok_text = case["expect"].lower() in blob.lower()
    return (ok_err and ok_text), res


def main():
    passed = 0
    print(f"{'ID':<5} {'Group':<15} {'Expect':<30} Verdict")
    print("-" * 80)
    for c in TESTS:
        ok, res = run_one(c)
        passed += ok
        trace = {"ts": datetime.now(timezone.utc).isoformat(), "week": 4,
                 "test": c["id"], "group": c["group"], "tool": c["tool"],
                 "result": res, "verdict": "PASS" if ok else "FAIL"}
        TRACE_DIR.mkdir(parents=True, exist_ok=True)
        (TRACE_DIR / f"{c['id']}.json").write_text(json.dumps(trace, indent=2))
        print(f"{c['id']:<5} {c['group']:<15} {c['expect'][:28]:<30} {'PASS' if ok else 'FAIL'}")
    print("-" * 80)
    print(f"{passed}/{len(TESTS)} pass. Traces W*.json in evidence/traces/")
    # revert any approval side effects from W04
    ap = BASE / "data" / "approvals.json"
    if ap.exists():
        ap.write_text("{}", encoding="utf-8")


if __name__ == "__main__":
    main()
