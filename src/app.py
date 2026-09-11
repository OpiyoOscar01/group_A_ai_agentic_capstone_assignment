"""
Week 2 baseline – University Student-Support Case Agent
Group A Day | BSE4104 | Model: gemini-2.0-flash | Prompt: prompts/v2.0.system.txt

Run:
  pip install -r requirements.txt
  copy .env.example .env  (add GEMINI_API_KEY – else MOCK mode)
  python src/app.py --chat
  python src/app.py --run-tests
  python src/app.py --message "Status of CASE-1001?"

Design (matches AI Boundary Matrix):
- LLM only suggests intent + draft text. Deterministic Python enforces:
  ID validation, timetable/case lookup from synthetic JSON, human-approval gate,
  out-of-scope block list, trace logging.
"""
import argparse, json, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PROMPT_FILE = BASE / "prompts" / "v2.0.system.txt"
TIMETABLE_FILE = BASE / "data" / "timetable.json"
CASES_FILE = BASE / "data" / "cases.json"
TRACE_DIR = BASE / ".." / ".." / "evidence" / "traces"  # Week2/evidence/traces if run from baseline
TRACE_DIR2 = BASE / "evidence" / "traces"  # fallback local
TESTS_FILE = BASE / "tests" / "week2_10cases.json"

OUT_OF_SCOPE_KW = ["admit", "admission", "grade change", "change my grade",
                   "increase my marks", "disciplinary", "tuition fee waiver",
                   "fee waiver", "expel", "suspend me"]
INJECTION_KW = ["ignore rules", "ignore previous", "approve", "resolved", "override"]

def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def validate_student_id(sid: str | None) -> bool:
    return bool(sid and re.fullmatch(r"(23|24)\d{8}", sid.strip()))

def validate_case_id(cid: str | None) -> bool:
    return bool(cid and re.fullmatch(r"CASE-\d{4}", cid.strip().upper()))

def extract_ids(msg: str):
    sid = re.search(r"\b(23|24)\d{8}\b", msg)
    cid = re.search(r"CASE-\d{4}", msg, re.IGNORECASE)
    return (sid.group(0) if sid else None,
            cid.group(0).upper() if cid else None)

def deterministic_lookup(intent_hint: str, sid, cid, session):
    """Stub tools for Week 2 – real DB/RAG comes Week 3/4."""
    try:
        tt = json.loads(TIMETABLE_FILE.read_text())
        cases = json.loads(CASES_FILE.read_text())
    except FileNotFoundError:
        tt, cases = {}, {}
    if sid and sid in tt:
        return {"tool": "timetable_lookup", "result": tt[sid]}
    active = cid or session.get("active_case_id")
    if active and active in cases:
        return {"tool": "case_status_lookup", "result": cases[active]}
    return {"tool": "none", "result": None}

def call_gemini(system: str, user_msg: str) -> tuple[str, int]:
    """Returns (text, latency_ms). Mock fallback if no key / no lib."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    start = time.time()
    if not api_key:
        return mock_response(user_msg), int((time.time() - start) * 1000)
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash",
                                      system_instruction=system)
        resp = model.generate_content(user_msg,
                                      generation_config={"temperature": 0.2,
                                                         "max_output_tokens": 400})
        return (resp.text or ""), int((time.time() - start) * 1000)
    except Exception as e:
        return mock_response(user_msg, error=str(e)), int((time.time() - start) * 1000)

def mock_response(msg: str, error: str | None = None) -> str:
    """Deterministic mock that already follows v2.0 JSON schema."""
    m = msg.lower()
    def j(intent, answer, cat=None, human=False, office=None):
        return json.dumps({"intent": intent, "answer": answer,
                           "suggested_category": cat, "needs_human": human,
                           "redirect_office": office})
    if any(k in m for k in ["ignore rules", "approve case", "mark as resolved", "approve ", "as resolved"]):
        return j("out_of_scope", "I cannot approve or resolve cases. Only staff can change status beyond Pending. Your case stays Pending for human review.", None, True, "Department Office")
    if any(k in m for k in ["change my grade", "admit me", "admission", "fee waiver", "disciplinary"]):
        return j("out_of_scope", "This is outside what I can help with. Please contact the Examinations Office / Admissions Office directly.", None, True, "Examinations / Admissions Office")
    if any(k in m for k in ["other student", "give me records", "records for student"]):
        return j("out_of_scope", "I can't share another student's records without authorization. See our Data Handling Note – I only use your own synthetic case data for your request.", None, True, "Department Office")
    if any(k in m for k in ["retake policy", "regulation", "policy for"]):
        return j("policy_qa", "[UNGROUNDED BASELINE] I don't know from approved documents yet (Week 3 RAG will add sources). In general, see your department office for the official retake regulation.", None, False, None)
    if any(k in m for k in ["missing marks", "submit my case", "create case", "registration issue", "retake request"]):
        return j("case_create", "I can draft your case. Please confirm name, student ID, category and description before I submit it as Pending for staff review.", "missing_marks", True, None)
    if "timetable" in m or re.search(r"\b(23|24)\d{8}\b", msg):
        return j("timetable", "[MOCK] Timetable lookup will be filled by deterministic code from data/timetable.json.", None, False, None)
    if "case-" in m or "status" in m or "my case" in m:
        return j("case_status", "[MOCK] Case status lookup will be filled by deterministic code.", None, False, None)
    if m.strip() in ["hello", "hi", "", "hey"]:
        return j("clarify", "Hello! I can help with policy questions, timetable, case status, or submitting a case. What do you need?", None, False, None)
    if not re.search(r"\b(23|24)\d{8}\b", msg) and ("id" in m or "123" in m):
        return j("clarify", "Invalid ID format. Makerere student ID is 10 digits starting 23/24, e.g. 2300701330. Please re-enter.", None, False, None)
    return j("clarify", "Could you clarify – are you asking a policy question, checking timetable/case status, or submitting a new case?", None, False, None)

def parse_llm(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {"intent": "clarify", "answer": text[:500], "suggested_category": None,
                "needs_human": False, "redirect_office": None, "_parse": "fallback"}
    try:
        d = json.loads(m.group(0))
        d.setdefault("suggested_category", None)
        d.setdefault("needs_human", False)
        d.setdefault("redirect_office", None)
        return d
    except json.JSONDecodeError:
        return {"intent": "clarify", "answer": text[:500], "suggested_category": None,
                "needs_human": False, "redirect_office": None, "_parse": "fallback"}

def handle_message(msg: str, session: dict, prompt_version="v2.0") -> dict:
    sid, cid = extract_ids(msg)
    if cid and validate_case_id(cid):
        session["active_case_id"] = cid
    # deterministic safety first
    low = msg.lower()
    if any(k in low for k in OUT_OF_SCOPE_KW):
        out = {"intent": "out_of_scope",
               "answer": "This request is outside what I can do (admissions/grading/disciplinary/fee). Please contact the relevant office – e.g. Admissions, Examinations, or Dean of Students. I have not taken any action.",
               "suggested_category": None, "needs_human": True,
               "redirect_office": "Admissions / Examinations / Dean of Students",
               "_guard": "deterministic-boundary"}
        tool = {"tool": "none", "result": None}
        lat = 0
    elif "123" in msg and not validate_student_id(sid or ""):
        out = {"intent": "clarify",
               "answer": "Invalid ID format. Use 10 digits starting 23/24, e.g. 2300701330.",
               "suggested_category": None, "needs_human": False,
               "redirect_office": None, "_guard": "deterministic-id-check"}
        tool = {"tool": "none", "result": None}
        lat = 0
    else:
        system = load_text(PROMPT_FILE).replace("{active_case_id}", str(session.get("active_case_id"))).replace("{student_id}", str(sid))
        raw, lat = call_gemini(system, msg)
        out = parse_llm(raw)
        out["_raw"] = raw[:1000]
        # deterministic enrichment: never let LLM invent timetable/case
        tool = deterministic_lookup(out.get("intent", ""), sid, cid, session)
        if tool["tool"] != "none":
            res = tool["result"]
            # attach id explicitly so traces are inspectable
            active_id = cid or session.get("active_case_id")
            if tool["tool"] == "timetable_lookup":
                out["_tool_result"] = {"student_id": sid, "record": res}
                codes = ", ".join(c.get("code", "") for c in res.get("classes", []))
                out["answer"] = f"{out['answer']} [Timetable for {sid}: {codes}]"
            else:
                out["_tool_result"] = {"case_id": active_id, "record": res}
                out["answer"] = f"{out['answer']} [Case {active_id} status: {res.get('status')}]"
        # hard guard: LLM must never claim approved/resolved
        if re.search(r"\b(approved|resolved|rejected)\b", out.get("answer", ""), re.I) and out.get("intent") != "out_of_scope":
            out["answer"] += " [Note: status changes beyond Pending require staff approval.]"
            out["needs_human"] = True
    trace = {"ts": datetime.now(timezone.utc).isoformat(), "prompt_version": prompt_version,
             "model": "gemini-2.0-flash", "input": msg, "session": dict(session),
             "output": out, "tool": tool, "latency_ms": lat}
    save_trace(trace)
    return trace

def save_trace(trace: dict):
    for d in (TRACE_DIR, TRACE_DIR2):
        try:
            d.mkdir(parents=True, exist_ok=True)
            n = len(list(d.glob("T*.json"))) + 1 if d.exists() else 1
            # avoid overwrite: use timestamp
            fn = d / f"trace_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}.json"
            fn.write_text(json.dumps(trace, indent=2), encoding="utf-8")
            break
        except OSError:
            continue

def run_tests():
    cases = json.loads(TESTS_FILE.read_text(encoding="utf-8"))
    session: dict = {}
    passed = partial = failed = 0
    print(f"{'ID':<5} {'Expect':<45} {'Got':<50} Verdict")
    print("-" * 120)
    for c in cases:
        # fresh session except T06 follow-up chain handled via 'session_setup'
        s = dict(c.get("session_setup", {})) if c.get("session_setup") else {}
        if c["id"] == "T06":
            s = {"active_case_id": "CASE-1001"}
        tr = handle_message(c["input"], s)
        ans = tr["output"].get("answer", "")
        exp = c["expected_contains"]
        ok = exp.lower() in ans.lower() or exp.lower() in json.dumps(tr["output"]).lower()
        verdict = "PASS" if ok else "FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"{c['id']:<5} {exp[:43]:<45} {ans[:48]:<50} {verdict}")
    print("-" * 120)
    print(f"Done: {passed} pass, {failed} fail out of {len(cases)}. Traces saved to evidence/traces/")

def chat_loop():
    session: dict = {}
    print("Makerere Support Agent – Week2 baseline (type 'quit' to exit, MOCK mode if no GEMINI_API_KEY)")
    while True:
        try: msg = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt): break
        if msg.lower() in ("quit", "exit"): break
        tr = handle_message(msg, session)
        print(f"\nAgent [{tr['output'].get('intent')}]: {tr['output'].get('answer')}")
        if tr["output"].get("redirect_office"): print(f"  -> Redirect: {tr['output']['redirect_office']}")
        if "_tool_result" in tr["output"]: print(f"  -> Tool [{tr['tool']['tool']}]: {json.dumps(tr['output']['_tool_result'])[:200]}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chat", action="store_true")
    ap.add_argument("--run-tests", action="store_true")
    ap.add_argument("--message", type=str, default=None)
    a = ap.parse_args()
    if a.run_tests: run_tests()
    elif a.message:
        print(json.dumps(handle_message(a.message, {}), indent=2))
    else: chat_loop()
