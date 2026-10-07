"""
Week 6 - Persistent memory: the student's ACTIVE CASE ID, and nothing else.
Group A | BSE4104 | see docs/design/Week6_Memory_Design_and_Data_Handling_Note.docx

Justified use case: a student comes back in a later session and asks
"what is the status of my case?" without retyping the case ID.

Design rules (enforced here, in code):
  * One record per student: {active_case_id, source, set_at, expires_at}. No message text,
    name, description, draft, approval or model output is ever stored.
  * Written only by the controller (agent.py) after a case is created or the student cites
    their OWN case. No model-callable action writes memory.
  * Keyed by the authenticated student_id. A record is only ever read for that same student.
  * Retention: 30 days, or until the case is no longer open, or until the student asks to
    forget it (whichever comes first). Expired / malformed records are deleted on read.
  * Every read, write and delete is logged to memory_audit.jsonl WITHOUT content
    (timestamp, student_id, operation, case_id, outcome/reason).
  * Memory is a hint, never an authority: the agent re-checks the case with the read-only
    lookup tool (which enforces ownership) before using it, and the planner never sees it.
"""
import json
import os
import re
import tempfile
from datetime import datetime, timedelta, timezone

import tools

TTL_DAYS = 30
ALLOWED_KEYS = {"active_case_id", "source", "set_at", "expires_at"}
ALLOWED_SOURCES = {"created", "cited"}


def _now():
    return datetime.now(timezone.utc)


class MemoryStore:
    def __init__(self, path=None, audit_path=None, now_fn=None):
        self._path = path
        self._audit_path = audit_path
        self._now = now_fn or _now

    # paths resolve at call time so tests can point tools.DATA at a temp copy
    @property
    def path(self):
        return self._path or os.path.join(tools.DATA, "memory.json")

    @property
    def audit_path(self):
        return self._audit_path or os.path.join(tools.DATA, "memory_audit.jsonl")

    # ---------------------------------------------------------------- file helpers
    def _load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self, data):
        d = os.path.dirname(self.path) or "."
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, self.path)          # atomic: no half-written memory file

    def _audit(self, student_id, op, case_id=None, outcome="ok"):
        line = {"ts": self._now().isoformat(), "student_id": student_id, "op": op,
                "case_id": case_id, "outcome": outcome}
        with open(self.audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(line) + "\n")

    # ---------------------------------------------------------------- public API
    def set_active_case(self, student_id, case_id, source):
        if not tools.STUDENT_ID_RE.match(student_id or "") or not tools.CASE_ID_RE.match(case_id or ""):
            self._audit(student_id, "write", case_id, "rejected_invalid_id")
            return False
        if source not in ALLOWED_SOURCES:
            self._audit(student_id, "write", case_id, "rejected_invalid_source")
            return False
        now = self._now()
        data = self._load()
        data[student_id] = {"active_case_id": case_id, "source": source, "set_at": now.isoformat(),
                            "expires_at": (now + timedelta(days=TTL_DAYS)).isoformat()}
        self._save(data)
        self._audit(student_id, "write", case_id, source)
        return True

    def get_active_case(self, student_id):
        """Return the record for THIS student, or None. Drops expired or malformed records."""
        data = self._load()
        entry = data.get(student_id)
        if entry is None:
            self._audit(student_id, "read", None, "miss")
            return None
        valid = (isinstance(entry, dict) and set(entry) == ALLOWED_KEYS
                 and tools.CASE_ID_RE.match(str(entry.get("active_case_id", "")))
                 and entry.get("source") in ALLOWED_SOURCES)
        if not valid:
            self.forget(student_id, "malformed_record")
            return None
        try:
            expired = datetime.fromisoformat(entry["expires_at"]) <= self._now()
        except (ValueError, TypeError):
            expired = True
        if expired:
            self.forget(student_id, "expired")
            return None
        self._audit(student_id, "read", entry["active_case_id"], "hit")
        return dict(entry)

    def forget(self, student_id, reason):
        data = self._load()
        entry = data.pop(student_id, None)
        if entry is not None:
            self._save(data)
        cid = entry.get("active_case_id") if isinstance(entry, dict) else None
        self._audit(student_id, "delete", cid, reason if entry is not None else f"{reason}:nothing_stored")
        return entry is not None
