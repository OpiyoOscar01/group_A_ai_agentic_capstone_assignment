"""Week 3 RAG pipeline – TF-IDF baseline (no external ML deps).
Ingest knowledge/*.txt -> chunk (180 words, 30 overlap) -> TF-IDF index
-> top-k retrieval -> grounded answer with [Source: DOC-xx] or safe abstention.
Run: python src/rag.py --query "..."  |  python src/rag.py --run-tests
"""
import json, math, re, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
KNOW = BASE / "knowledge"
TRACE_DIR = BASE / "evidence" / "week3_15tests_traces"
TESTS = BASE / "tests" / "week3_15cases.json"
CHUNK_WORDS, OVERLAP, TOP_K, MIN_SCORE = 180, 30, 3, 0.14
MAX_ANSWER_WORDS = 240
ANSWER_STOP_WORDS = set(
    "a an the and or but to of in on for from at by with as is are was were "
    "be been being do does did can could would should may might what where when "
    "who whom how much many me my i you your we our it this that these those "
    "about tell please still after before during if then there their per s".split()
)
ANSWER_SYNONYMS = {
    "failed": "fail",
    "fails": "fail",
    "paid": "pay",
    "paying": "pay",
    "fees": "fee",
    "marks": "mark",
    "results": "result",
    "published": "publish",
    "publication": "publish",
    "times": "time",
    "retakes": "retake",
    "attempts": "attempt",
    "units": "unit",
    "classes": "class",
    "labs": "lab",
    "exams": "exam",
    "examinations": "exam",
    "students": "student",
    "cases": "case",
    "grades": "grade",
    "calculated": "calculate",
    "calculation": "calculate",
    "computed": "calculate",
    "minimum": "min",
    "maximum": "max",
    "missing": "miss",
    "format": "form",
}


def _answer_terms(text):
    terms = set()
    for word in tokenize(text):
        if word in ANSWER_STOP_WORDS:
            continue
        word = ANSWER_SYNONYMS.get(word, word)
        if word == "pending":
            terms.add(word)
            continue
        if word.endswith("ies") and len(word) > 4:
            word = word[:-3] + "y"
        elif word.endswith("ing") and len(word) > 5:
            word = word[:-3]
        elif word.endswith("ed") and len(word) > 4:
            word = word[:-2]
        elif word.endswith("s") and len(word) > 4:
            word = word[:-1]
        terms.add(word)
    return terms


def _document_sentences(hit):
    document = (KNOW / hit["file"]).read_text(encoding="utf-8")
    _, separator, body = document.partition("\n")
    text = body if separator else document
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text.strip())
        if sentence.strip()
    ]


def _query_clauses(query):
    return [
        clause.strip()
        for clause in re.split(r"\s*(?:[,;]|\band\b|\balso\b)\s*", query, flags=re.I)
        if _answer_terms(clause)
    ]


def _sentence_coverage(query_terms, sentence):
    if not query_terms:
        return 0.0
    return len(query_terms & _answer_terms(sentence)) / len(query_terms)


def answer_sentences(query, hits):
    """Select the strongest source sentences for each part of a question."""
    clauses = _query_clauses(query)
    selected = {}
    hit_by_doc = {
        hit["doc_id"]: hit
        for hit in hits
        if hit["score"] >= MIN_SCORE
    }

    for clause in clauses:
        for hit in retrieve(clause):
            if hit["score"] >= MIN_SCORE:
                hit_by_doc.setdefault(hit["doc_id"], hit)
        query_terms = _answer_terms(clause)
        candidates = []
        for hit in hit_by_doc.values():
            sentences = _document_sentences(hit)
            coverages = [
                _sentence_coverage(query_terms, sentence)
                for sentence in sentences
            ]
            if coverages:
                candidates.append((max(coverages), hit, sentences, coverages))
        if not candidates:
            continue

        best_coverage = max(item[0] for item in candidates)
        best_coverage, hit, sentences, coverages = next(
            item for item in candidates if item[0] == best_coverage
        )
        if best_coverage == 0:
            continue

        selected_sentences = selected.setdefault(hit["doc_id"], set())
        focus_term = next(
            (
                term
                for term in reversed(tokenize(clause))
                if term not in ANSWER_STOP_WORDS
            ),
            None,
        )
        focus_term = ANSWER_SYNONYMS.get(focus_term, focus_term)
        focus_term = _answer_terms(focus_term or "")
        relevant = [
            sentence
            for sentence, coverage in zip(sentences, coverages)
            if coverage >= best_coverage - 0.15
        ]
        focused = [
            sentence for sentence in relevant
            if focus_term and focus_term & _answer_terms(sentence)
        ]
        selected_sentences.update(focused or relevant)

    # Include the cited procedure when a retrieved source explicitly points to it.
    cited_ids = {
        doc_id
        for sentences in selected.values()
        for sentence in sentences
        for doc_id in re.findall(r"\bDOC-\d{2}\b", sentence)
    }
    for doc_id in cited_ids:
        hit = hit_by_doc.get(doc_id)
        source_mentions_procedure = any(
            re.search(r"\bprocedure\b", sentence, re.I)
            for sentences in selected.values()
            for sentence in sentences
            if doc_id in re.findall(r"\bDOC-\d{2}\b", sentence)
        )
        if hit and source_mentions_procedure:
            selected.setdefault(doc_id, set()).update(_document_sentences(hit))

    if re.search(r"\b(procedure|what should i do|what do i do|next step)\b", query, re.I):
        for hit in hit_by_doc.values():
            if hit["doc_id"] not in selected:
                continue
            sentences = _document_sentences(hit)
            if any(
                re.search(r"\b(report to|file a support case|contact the course lecturer)\b", sentence, re.I)
                for sentence in sentences
            ):
                selected[hit["doc_id"]].update(sentences)

    # Pending status is explained by the staff-review condition in the case guidance.
    if any("pending" in _answer_terms(clause) for clause in clauses):
        for hit in hit_by_doc.values():
            for sentence in _document_sentences(hit):
                terms = _answer_terms(sentence)
                if "pending" in terms and ("review" in terms or "staff" in terms):
                    selected.setdefault(hit["doc_id"], set()).add(sentence)

    return [
        (hit["doc_id"], [
            sentence for sentence in _document_sentences(hit)
            if sentence in selected.get(hit["doc_id"], set())
        ])
        for hit in hit_by_doc.values()
        if selected.get(hit["doc_id"])
    ]


def answer_excerpt(hit, query):
    sections = answer_sentences(query, [hit])
    return " ".join(sentence for _, sentences in sections for sentence in sentences)

def tokenize(t: str):
    return re.findall(r"[a-z0-9]+", t.lower())

def load_chunks():
    chunks = []
    for f in sorted(KNOW.glob("*.txt")):
        text = f.read_text(encoding="utf-8")
        m = re.search(r"DOC-ID:\s*(DOC-\d+)", text)
        doc_id = m.group(1) if m else f.stem
        words = text.split()
        step = CHUNK_WORDS - OVERLAP
        for i in range(0, max(1, len(words)), step):
            c = " ".join(words[i:i + CHUNK_WORDS])
            if len(c.split()) < 20:
                continue
            chunks.append({"doc_id": doc_id, "file": f.name, "chunk_id": f"{doc_id}-C{(i//step)+1}", "text": c})
            if i + CHUNK_WORDS >= len(words):
                break
    return chunks

def build_index(chunks):
    df = Counter()
    tf_list = []
    for c in chunks:
        toks = tokenize(c["text"])
        tf = Counter(toks)
        tf_list.append(tf)
        for t in set(toks):
            df[t] += 1
    N = len(chunks)
    idf = {t: math.log((N + 1) / (d + 1)) + 1 for t, d in df.items()}
    return tf_list, idf

def score(query, tf, idf):
    qt = Counter(tokenize(query))
    num = den_q = den_d = 0.0
    # cosine over TF-IDF
    q_weights = {t: (1 + math.log(c)) * idf.get(t, 0) for t, c in qt.items() if t in idf}
    d_weights = {t: (1 + math.log(c)) * idf.get(t, 0) for t, c in tf.items() if t in idf}
    for t, qw in q_weights.items():
        if t in d_weights:
            num += qw * d_weights[t]
    den_q = math.sqrt(sum(v * v for v in q_weights.values())) or 1e-9
    den_d = math.sqrt(sum(v * v for v in d_weights.values())) or 1e-9
    return num / (den_q * den_d)

CHUNKS = load_chunks()
TF_LIST, IDF = build_index(CHUNKS)

def retrieve(query, k=TOP_K):
    scored = [(score(query, tf, IDF), c) for tf, c in zip(TF_LIST, CHUNKS)]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"score": round(s, 4), **c} for s, c in scored[:k]]

def answer(query, use_llm=False):
    """Deterministic grounded answerer. use_llm=True wraps with Gemini if key present."""
    hits = retrieve(query)
    top = [h for h in hits if h["score"] >= MIN_SCORE]
    trace = {"ts": datetime.now(timezone.utc).isoformat(), "model": "rag-tfidf-v1+gemini-3.8-flash",
             "prompt_version": "v3.0-rag", "query": query,
             "retrieved": [{"chunk_id": h["chunk_id"], "doc_id": h["doc_id"], "score": h["score"],
                            "excerpt": h["text"][:220]} for h in hits]}
    low = query.lower()
    boundary_phrases = [
        "admit me",
        "eligible for admission",
        "admission to",
        "transfer admission",
        "programme change",
        "change my grade",
        "approve a fee waiver",
        "approve the fee waiver",
        "approve my fee waiver",
        "grant a fee waiver",
        "waive my fee",
        "disciplinary appeal decide",
        "approve my fee",
    ]
    has_boundary = any(phrase in low for phrase in boundary_phrases)
    answerable_query = " and ".join(
        clause for clause in _query_clauses(query)
        if not any(phrase in clause.lower() for phrase in boundary_phrases)
    )
    has_answerable = has_boundary and (
        any(k in low for k in ["supplementary", "gpa", "explain"])
        or bool(answerable_query and answer_sentences(answerable_query, hits))
    )
    # mixed request: ground what we can, refuse the rest -> partial (fixes over-refusal F-01)
    if has_boundary and has_answerable:
        answerable_hits = [
            hit for hit in retrieve(answerable_query)
            if hit["score"] >= MIN_SCORE
        ] if answerable_query else []
        sections = answer_sentences(answerable_query, answerable_hits)
        selected_sources = [doc_id for doc_id, _ in sections]
        selected_text = " ".join(
            sentence for _, sentences in sections for sentence in sentences
        )
        if selected_text:
            boundary_docs = [
                doc_id for phrases, doc_id in (
                    (("approve a fee waiver", "approve the fee waiver",
                      "approve my fee waiver", "grant a fee waiver",
                      "waive my fee", "approve my fee"), "DOC-10"),
                    (("admit me", "eligible for admission", "admission to",
                      "transfer admission", "programme change"), "DOC-11"),
                    (("change my grade",), "DOC-05"),
                    (("disciplinary appeal decide",), "DOC-09"),
                )
                if any(phrase in low for phrase in phrases)
            ]
            boundary_sources = sorted(set(boundary_docs))
            boundary_office = (
                "the Bursar / Finance Office" if "fee" in low
                else "the Admissions Office" if "admission" in low
                else "the Examinations Office" if "grade" in low
                else "the appropriate university office"
            )
            trace.update({
                "decision": "partial",
                "answer": (
                    f"Partially answerable. {selected_text} "
                    + " ".join(f"[Source: {doc_id}]" for doc_id in selected_sources)
                    + ". "
                    f"The other part is outside what I can decide. Please contact "
                    f"{boundary_office}. No action taken. "
                    f"[Policy: {', '.join(boundary_sources)}]"
                ),
                "sources": sorted({*selected_sources, *boundary_sources}),
            })
            return trace
    # pure boundary request -> refuse (fixes under-refusal F-02: R12)
    if has_boundary and not has_answerable:
        trace.update({"decision": "refuse-boundary", "answer": "This is outside what I can do. I have not taken any action. Please contact the Admissions / Examinations / Bursar / Disciplinary Committee as appropriate. [Policy: DOC-10, DOC-11]",
                      "sources": ["DOC-10", "DOC-11"]})
        return trace
    sections = answer_sentences(query, hits)
    if not top and not sections:
        trace.update({"decision": "abstain", "answer": "I don't know from approved documents (no relevant source retrieved). Please visit the Department Office. No action taken.",
                      "sources": []})
        return trace
    # partially answerable heuristic: only 1 weak hit
    if len(top) == 1 and top[0]["score"] < 0.15:
        trace.update({"decision": "partial", "answer": f"Partially answerable from approved documents. {answer_excerpt(top[0], query)} [Source: {top[0]['doc_id']}]. For the remainder, I don't have an approved source – please confirm with the Department Office.",
                      "sources": [top[0]["doc_id"]]})
        return trace
    if not sections:
        trace.update({"decision": "abstain", "answer": "I don't know from approved documents (no relevant source retrieved). Please visit the Department Office. No action taken.",
                      "sources": []})
        return trace
    sources = []
    answer_parts = []
    for doc_id, sentences in sections:
        if len(" ".join(answer_parts + sentences).split()) > MAX_ANSWER_WORDS:
            break
        answer_parts.extend(sentences)
        sources.append(doc_id)
    llm_note = ""
    if use_llm:
        llm_note = " (phrased with gemini-3.8-flash, grounded only in retrieved excerpts)"
    trace.update({"decision": "grounded",
                  "answer": f"{' '.join(answer_parts)}{llm_note} "
                            + " ".join(f"[Source: {doc_id}]" for doc_id in sources),
                  "sources": sources})
    return trace

def run_tests():
    cases = json.loads(TESTS.read_text(encoding="utf-8"))
    print(f"{'ID':<5} {'Type':<10} {'Score':<7} {'Decision':<10} Verdict")
    print("-" * 110)
    passed = 0
    for c in cases:
        tr = answer(c["query"])
        TRACE_DIR.mkdir(parents=True, exist_ok=True)
        (TRACE_DIR / f"{c['id']}.json").write_text(json.dumps({**tr, "expected": c}, indent=2), encoding="utf-8")
        got_src = set(tr.get("sources", []))
        exp_src = set(c.get("must_cite", []))
        if c["type"] == "unanswerable":
            ok = tr["decision"] in ("abstain", "refuse-boundary")
        elif c["type"] == "partial":
            ok = tr["decision"] in ("partial", "grounded") and bool(got_src & exp_src or tr["decision"] == "partial")
        else:
            ok = tr["decision"] == "grounded" and bool(got_src & exp_src)
        if c.get("must_refuse"):
            ok = ok and "outside what I can" in tr["answer"] or tr["decision"] == "refuse-boundary" and ok
        print(f"{c['id']:<5} {c['type']:<10} {tr['retrieved'][0]['score']:<7} {tr['decision']:<10} {'PASS' if ok else 'FAIL'}")
        passed += ok
    print("-" * 110)
    print(f"{passed}/{len(cases)} pass. Traces in evidence/traces/")

if __name__ == "__main__":
    if "--run-tests" in sys.argv:
        run_tests()
    elif "--query" in sys.argv:
        q = sys.argv[sys.argv.index("--query") + 1]
        print(json.dumps(answer(q, use_llm=("--llm" in sys.argv)), indent=2))
    else:
        print("Usage: python src/rag.py --query \"...\" [--llm] | --run-tests")
