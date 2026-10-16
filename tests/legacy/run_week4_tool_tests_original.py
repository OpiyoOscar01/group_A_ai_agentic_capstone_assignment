"""
Week 4 - Failure/authorization test runner (Quality/Security Lead: Isio Lily)
Runs tests/week4_tool_tests.json against src/tools.py and writes one evidence
trace per case to evidence/week4_traces/T01.json ... T10.json, per the test matrix
in docs/architecture/Week4_01_Tool_Catalogue.docx Section 4.
"""
import json
import os
import shutil
import sys
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "src"))
import tools  # noqa: E402

CASES_PATH = os.path.join(BASE, "data", "cases.json")


def run_one(case):
    args = dict(case["args"])
    simulate_outage = args.pop("__simulate_outage", False)
    backup = None

    if simulate_outage:
        backup = CASES_PATH + ".bak"
        shutil.move(CASES_PATH, backup)

    try:
        fn = getattr(tools, case["tool"])
        result = fn(**args)
    finally:
        if simulate_outage and backup:
            shutil.move(backup, CASES_PATH)

    ok = True
    if "expect_error" in case:
        ok = result.get("error_code") == case["expect_error"]
    elif "expect_status" in case:
        ok = result.get("status") == case["expect_status"]

    trace = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "id": case["id"], "name": case["name"], "tool": case["tool"],
        "args": case["args"], "result": result, "verdict": "PASS" if ok else "FAIL"
    }
    with open(os.path.join(BASE, "evidence", "week4_traces", f"{case['id']}.json"), "w") as f:
        json.dump(trace, f, indent=2)
    return trace


def main():
    with open(os.path.join(BASE, "tests", "week4_tool_tests.json")) as f:
        cases = json.load(f)

    print(f"{'ID':<5}{'Test':<55}{'Verdict':<8}")
    print("-" * 70)
    passed = 0
    for c in cases:
        t = run_one(c)
        print(f"{t['id']:<5}{t['name']:<55}{t['verdict']:<8}")
        passed += (t["verdict"] == "PASS")
    print("-" * 70)
    print(f"{passed}/{len(cases)} passed. week4_traces in evidence/week4_traces/")


if __name__ == "__main__":
    main()
