"""
Week 6 - Working memory / state demonstration + interface conformance check.

Scenarios (each runs on its OWN temporary copy of data/, real files are never touched):
  M1 recall_across_sessions        memory improves a legitimate task (fewer turns), survives a "restart"
  M2 memory_does_not_decide        memory never skips the duplicate check or the approval gate; planner never sees it
  M3 stale_memory_dropped          a case staff have closed is no longer treated as active
  M4 deletion_on_request           "forget my session" removes the record; later follow-up asks for the ID
  M5 tampered_memory_rejected      a record pointing at ANOTHER student's case is refused and deleted, nothing leaks
  M6 expiry                        records older than 30 days are ignored and deleted
  M7 data_minimisation             only 4 fields stored, no free text; no model-callable action writes memory
  I1 interface_matches_code        docs/interfaces manifest agrees with the real validator/tool constants

Run:  python tests/run_week6_memory_demo.py     -> evidence/week6_memory/*.json|md + SUMMARY.md
"""
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))
import tools  # noqa: E402
import agent as A  # noqa: E402
from memory import MemoryStore, ALLOWED_KEYS, TTL_DAYS  # noqa: E402

OUT = BASE / "evidence" / "week6_memory"
HAPPY = ["My BSE4104 marks are missing.",
         "I reported it to Dr Kato 10 days ago, semester 2026-S1.",
         "I have my exam card and the signed attendance sheet.",
         "yes"]
CHRISTINE, OSCAR = "2300701098", "2300701330"


class World:
    """A fresh temp copy of data/ plus a transcript recorder."""
    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="w6_"))
        shutil.copytree(BASE / "data", self.tmp / "data")
        self.data = self.tmp / "data"
        tools.DATA = str(self.data)
        self.transcript, self.checks = [], []

    def say(self, agent, session, msg, label=None):
        self.transcript.append({"who": f"student{(' ' + label) if label else ''}", "text": msg})
        r = agent.handle_turn(session, msg)
        self.transcript.append({"who": "agent", "text": r["message"]})
        return r

    def check(self, desc, cond):
        self.checks.append({"check": desc, "pass": bool(cond)})
        return bool(cond)

    def cases(self):
        return json.loads((self.data / "cases.json").read_text())

    def memory_file(self):
        p = self.data / "memory.json"
        return json.loads(p.read_text()) if p.exists() else {}

    def audit(self):
        p = self.data / "memory_audit.jsonl"
        return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def seeded_world():
    """Christine completes the happy path in 'session A', so a new case exists and memory holds its ID."""
    w = World()
    agent, sess = A.Agent(), A.Session(CHRISTINE)
    for m in HAPPY:
        w.say(agent, sess, m, "(session A)")
    w.case_id = sess.last_run.created_case_id          # whatever ID the store assigns; never hard-coded
    assert w.case_id and sess.last_run.stop_reason == "GOAL_MET", "seed failed"
    return w


def new_session_after_restart(student):
    """New Agent, new MemoryStore object, new Session: nothing survives except what is on disk."""
    return A.Agent(memory=MemoryStore()), A.Session(student)


# ------------------------------------------------------------------ scenarios
def m1():
    w = seeded_world()
    # baseline: the same question with NO memory takes two turns
    base_mem = MemoryStore(path=str(w.tmp / "none.json"), audit_path=str(w.tmp / "none_audit.jsonl"))
    b_agent, b_sess = A.Agent(memory=base_mem), A.Session(CHRISTINE)
    n0 = len(w.transcript)
    r1 = w.say(b_agent, b_sess, "What is the status of my case?", "(baseline, no memory)")
    r2 = w.say(b_agent, b_sess, f"Check status of {w.case_id}", "(baseline, no memory)")
    baseline_turns = (len(w.transcript) - n0) // 2          # measured, not assumed
    # with memory, in a brand-new session after a restart
    agent, sess = new_session_after_restart(CHRISTINE)
    n1 = len(w.transcript)
    r = w.say(agent, sess, "What is the status of my case?", "(session B, next day)")
    memory_turns = (len(w.transcript) - n1) // 2
    w.check("memory record persisted to disk after the case was created",
            w.memory_file().get(CHRISTINE, {}).get("active_case_id") == w.case_id)
    w.check("baseline without memory had to ask for the case ID", "case ID" in r1["message"] and not r1.get("memory_used"))
    w.check("with memory the answer names the remembered case and its live status (Pending) in ONE turn",
            w.case_id in r["message"] and "Pending" in r["message"] and r.get("memory_used") is True)
    w.check(f"turns needed (measured): {memory_turns} with memory < {baseline_turns} without", memory_turns < baseline_turns)
    w.check("status shown came from a live lookup, not from stored text (record holds no status)",
            "status" not in w.memory_file()[CHRISTINE])
    out = ("M1", "recall_across_sessions", "Memory improves a legitimate task: status follow-up in 1 turn instead of 2, across a restart", w)
    return out


def m2():
    w = seeded_world()
    cases_before = len(w.cases())
    reads_before = sum(1 for e in w.audit() if e["op"] == "read")
    agent, sess = new_session_after_restart(CHRISTINE)
    r = w.say(agent, sess, "My BSE4104 marks are missing.", "(session B)")
    run = sess.last_run
    w.check("same request again -> DUPLICATE_FOUND from the LIVE my_cases lookup (memory did not decide)",
            r["stop_reason"] == "DUPLICATE_FOUND" and any(e["type"] == "act" and e.get("action") == "lookup_case_or_timetable"
                                                          and e["args"].get("query_type") == "my_cases" for e in run.events))
    w.check("no new case created", len(w.cases()) == cases_before)
    w.check("the case-preparation run never read memory (no new 'read' in the audit log)",
            sum(1 for e in w.audit() if e["op"] == "read") == reads_before)
    w.check("the planner's state summary never contains memory (no active_case_id key in any SENSE event)",
            all("active_case_id" not in e["summary"] for e in run.events if e["type"] == "sense"))
    # a different request still has to go through the approval gate
    agent2, sess2 = new_session_after_restart(CHRISTINE)
    r2 = w.say(agent2, sess2, "I need to retake BIT2101, semester 2026-S1", "(session C)")
    w.check("a new request with memory present still stops at AWAITING_APPROVAL (memory is not an approval)",
            r2["stop_reason"] == "AWAITING_APPROVAL" and len(w.cases()) == cases_before)
    r3 = w.say(agent2, sess2, "no", "(session C)")
    w.check("declining leaves the case store unchanged", r3["stop_reason"] == "APPROVAL_DECLINED" and len(w.cases()) == cases_before)
    return ("M2", "memory_does_not_decide", "Memory does not silently control critical decisions", w)


def m3():
    w = seeded_world()
    cases = w.cases()
    for c in cases:
        if c["case_id"] == w.case_id:
            c["status"] = "Resolved"                       # staff close the case (simulated)
    (w.data / "cases.json").write_text(json.dumps(cases, indent=2))
    agent, sess = new_session_after_restart(CHRISTINE)
    r = w.say(agent, sess, "What is the status of my case?", "(session B)")
    w.check("reply says the case is Resolved and no longer active", "Resolved" in r["message"] and "no longer" in r["message"])
    w.check("memory record deleted", CHRISTINE not in w.memory_file())
    w.check("audit log records deletion reason case_closed", any(e["op"] == "delete" and e["outcome"] == "case_closed" for e in w.audit()))
    return ("M3", "stale_memory_dropped", "A closed case is no longer treated as active", w)


def m4():
    w = seeded_world()
    agent, sess = new_session_after_restart(CHRISTINE)
    r = w.say(agent, sess, "Please forget my session", "(session B)")
    w.check("student can delete the record on request", "Done" in r["message"] and CHRISTINE not in w.memory_file())
    agent2, sess2 = new_session_after_restart(CHRISTINE)
    r2 = w.say(agent2, sess2, "What is the status of my case?", "(session C)")
    w.check("after deletion the agent asks for the ID instead of guessing", "case ID" in r2["message"] and not r2.get("memory_used"))
    w.check("audit log records student_request deletion", any(e["op"] == "delete" and e["outcome"] == "student_request" for e in w.audit()))
    return ("M4", "deletion_on_request", "Deletion on request works and is final", w)


def m5():
    w = World()
    lily_case = next(c for c in w.cases() if c["case_id"] == "CASE-0001")
    MemoryStore().set_active_case(OSCAR, "CASE-0001", "cited")      # tampered: Oscar's record points at Lily's case
    agent, sess = A.Agent(memory=MemoryStore()), A.Session(OSCAR)
    r = w.say(agent, sess, "What is the status of my case?", "(Oscar)")
    leaked = [v for k, v in lily_case.items() if k in ("name", "description", "student_id") and str(v).lower() in r["message"].lower()]
    w.check("the lookup tool refused the other student's case and nothing from it appears in the reply", not leaked and "CASE-0001" not in r["message"])
    w.check("the bad record was deleted", OSCAR not in w.memory_file())
    w.check("audit log shows the discard reason lookup_UNAUTHORIZED", any(e["op"] == "delete" and e["outcome"] == "lookup_UNAUTHORIZED" for e in w.audit()))
    return ("M5", "tampered_memory_rejected", "Memory cannot be used to read another student's case", w)


def m6():
    w = seeded_world()
    mem = w.memory_file()
    mem[CHRISTINE]["expires_at"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    mem[CHRISTINE]["set_at"] = (datetime.now(timezone.utc) - timedelta(days=TTL_DAYS + 1)).isoformat()
    (w.data / "memory.json").write_text(json.dumps(mem))
    agent, sess = new_session_after_restart(CHRISTINE)
    r = w.say(agent, sess, "What is the status of my case?", "(session B, 31 days later)")
    w.check("expired record ignored: agent asks for the ID", "case ID" in r["message"] and not r.get("memory_used"))
    w.check("expired record deleted with reason 'expired'", CHRISTINE not in w.memory_file() and any(e["op"] == "delete" and e["outcome"] == "expired" for e in w.audit()))
    return ("M6", "expiry", f"Records older than {TTL_DAYS} days are not used", w)


def m7():
    w = seeded_world()
    entry = w.memory_file()[CHRISTINE]
    raw = (w.data / "memory.json").read_text().lower()
    w.check("stored record has exactly the 4 allowed fields", set(entry) == ALLOWED_KEYS)
    w.check("no free text stored (no name, description, course code, message text or draft)",
            not any(t in raw for t in ("namatovu", "marks", "bse4104", "exam card", "dr kato", "reported")))
    w.check("audit log lines contain no content fields", all(set(e) == {"ts", "student_id", "op", "case_id", "outcome"} for e in w.audit()))
    w.check("no model-callable action touches memory (the six allowed actions are fixed)",
            set(A.ACTIONS) == {"search_handbook", "lookup_case_or_timetable", "ask_student", "present_draft",
                               "create_draft_support_case", "finish", "handoff"})
    sites = [(f.name, l) for f in (BASE / "src").glob("*.py") if f.name != "memory.py"
             for l in f.read_text().splitlines() if "set_active_case(" in l]
    w.check("the ONLY call site that writes memory is the controller's _remember helper (agent.py)", len(sites) == 1 and sites[0][0] == "agent.py")
    return ("M7", "data_minimisation", "Only the justified field is stored", w)


def i1():
    w = World()
    man = json.loads((BASE / "docs" / "interfaces" / "support_case_mcp_manifest.json").read_text())
    tl = {t["name"]: t for t in man["tools"]}
    code_tools = {n for n, s in A.ACTIONS.items() if s["kind"] == "tool"}
    w.check("manifest tools == the agent's tool actions", set(tl) == code_tools)
    for n, t in tl.items():
        props, req = set(t["inputSchema"]["properties"]), set(t["inputSchema"]["required"])
        w.check(f"{n}: model-visible args and required args match the validator", props == A.ACTIONS[n]["allowed"] and req == A.ACTIONS[n]["required"])
        w.check(f"{n}: student_id / approved are not model-visible", not ({"student_id", "approved"} & props))
    w.check("category enum == code ALLOWED_CATEGORIES",
            set(tl["create_draft_support_case"]["inputSchema"]["properties"]["category"]["enum"]) == A.ALLOWED_CATEGORIES)
    w.check("query_type enum == code AGENT_QUERY_TYPES",
            set(tl["lookup_case_or_timetable"]["inputSchema"]["properties"]["query_type"]["enum"]) == A.AGENT_QUERY_TYPES)
    w.check("description maxLength == code limit",
            tl["create_draft_support_case"]["inputSchema"]["properties"]["description"]["maxLength"] == A.LIMITS["max_description_chars"])
    src = open(BASE / "src" / "tools.py").read()
    codes = set(re.findall(r'"error_code": "([A-Z_]+)"', src)) | {"NO_SOURCE"}
    w.check("every documented error code exists in the tool code", all(set(t["x-errors"]) <= codes for t in tl.values()))
    w.check("read-only hints: search and lookup read-only, create is not",
            tl["search_handbook"]["annotations"]["readOnlyHint"] and tl["lookup_case_or_timetable"]["annotations"]["readOnlyHint"]
            and not tl["create_draft_support_case"]["annotations"]["readOnlyHint"])
    r = tools.create_draft_support_case(CHRISTINE, "X", "other", "d", approved=False)
    w.check("behaviour matches spec: create without host approval -> APPROVAL_DECLINED", r.get("error_code") == "APPROVAL_DECLINED")
    w.check("memory store is declared as not exposed", any("memory" in x for x in man["not_exposed"]))
    return ("I1", "interface_matches_code", "The MCP-style specification agrees with the implementation", w)


SCENARIOS = [m1, m2, m3, m4, m5, m6, m7, i1]


def render_md(sid, slug, title, w, verdict):
    L = [f"# {sid} - {title}\n", f"**Verdict: {verdict}**\n", "## Conversation\n"]
    for t in w.transcript:
        L.append(f"- **{t['who']}:** {t['text']}")
    if w.transcript:
        L.append("")
    L.append("## Checks\n")
    for c in w.checks:
        L.append(f"- {'PASS' if c['pass'] else 'FAIL'}: {c['check']}")
    L.append("\n## Memory file at the end of the scenario (data/memory.json)\n")
    L.append("```json\n" + json.dumps(w.memory_file(), indent=2) + "\n```")
    L.append("\n## Memory audit log (content-free)\n")
    for e in w.audit():
        L.append(f"- {e['ts'][11:19]} {e['student_id']} {e['op']} {e['case_id']} {e['outcome']}")
    return "\n".join(L) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*"):
        old.unlink()
    rows = []
    for fn in SCENARIOS:
        sid, slug, title, w = fn()
        verdict = "PASS" if w.checks and all(c["pass"] for c in w.checks) else "FAIL"
        stem = f"{sid}_{slug}"
        (OUT / f"{stem}.json").write_text(json.dumps({"id": sid, "title": title, "verdict": verdict, "transcript": w.transcript,
                                                       "checks": w.checks, "memory_file": w.memory_file(), "audit": w.audit()}, indent=2))
        (OUT / f"{stem}.md").write_text(render_md(sid, slug, title, w, verdict), encoding="utf-8")
        rows.append((sid, title, sum(c["pass"] for c in w.checks), len(w.checks), verdict))
        w.close()
    print(f"{'ID':<5}{'Checks':<9}{'Verdict':<8}Scenario\n" + "-" * 90)
    for r in rows:
        print(f"{r[0]:<5}{r[2]}/{r[3]:<7}{r[4]:<8}{r[1]}")
    n = sum(r[4] == "PASS" for r in rows)
    print("-" * 90 + f"\n{n}/{len(rows)} scenarios pass, {sum(r[2] for r in rows)}/{sum(r[3] for r in rows)} checks. Evidence: {OUT.relative_to(BASE)}")
    md = ["# Week 6 memory and interface demonstration - summary\n", "| ID | Scenario | Checks | Verdict |", "|---|---|---|---|"]
    md += [f"| {r[0]} | {r[1]} | {r[2]}/{r[3]} | {r[4]} |" for r in rows]
    (OUT / "SUMMARY.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    sys.exit(0 if n == len(rows) else 1)


if __name__ == "__main__":
    main()
