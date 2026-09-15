# RAG Architecture Diagram
## University Student-Support Case Agent

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           STUDENT QUERY                                         │
│                    "What is the retake policy for failed courses?"              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         FLASK APPLICATION (app.py)                              │
│                                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Receive    │───►│   Extract    │───►│   Retrieve   │───►│   Generate   │  │
│  │    Query     │    │  Intent      │    │   Context    │    │   Response   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │                   │
│                                                             ▼                   │
│                                                    ┌──────────────┐            │
│                                                    │   Response   │            │
│                                                    │   + Sources  │            │
│                                                    └──────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│   RETRIEVAL MODULE    │ │   GEMINI MODEL        │ │   SYNTHETIC DATA     │
│   (Oscar's code)      │ │   (gemini-3.6-flash)  │ │   (timetable/cases)  │
│                       │ │                       │ │                       │
│  ┌─────────────────┐  │ │  ┌─────────────────┐  │ │  ┌─────────────────┐  │
│  │  Ingestion &    │  │ │  │  System Prompt  │  │ │  │  timetable.json │  │
│  │  Chunking       │  │ │  │  + Retrieved    │  │ │  │  cases.json     │  │
│  │                 │  │ │  │  Context        │  │ │  │                 │  │
│  └─────────────────┘  │ │  └─────────────────┘  │ │  └─────────────────┘  │
│           │          │ │           │          │ │           │          │
│           ▼          │ │           ▼          │ │           ▼          │
│  ┌─────────────────┐  │ │  ┌─────────────────┐  │ │                       │
│  │  Indexing       │  │ │  │  Generate       │  │ │                       │
│  │  (TF-IDF/       │  │ │  │  Grounded      │  │ │                       │
│  │   Embeddings)   │  │ │  │  Answer        │  │ │                       │
│  └─────────────────┘  │ │  └─────────────────┘  │ │                       │
│           │          │ │           │          │ │                       │
│           ▼          │ │           ▼          │ │                       │
│  ┌─────────────────┐  │ │  ┌─────────────────┐  │ │                       │
│  │  Top-k          │  │ │  │  Response with  │  │ │                       │
│  │  Retrieval      │  │ │  │  Source Citations│  │ │                       │
│  │                 │  │ │  │  [Source: DOC-xx]│  │ │                       │
│  └─────────────────┘  │ │  └─────────────────┘  │ │                       │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DOCUMENT CORPUS                                    │
│                                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐│
│  │  DOC-01     │ │  DOC-02     │ │  DOC-03     │ │  DOC-04     │ │  DOC-xx   ││
│  │  Academic   │ │  Student    │ │  Course     │ │  Handbook   │ │  ...      ││
│  │  Regulations│ │  Handbook   │ │  Syllabus   │ │  Appendix   │ │           ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘│
│                                                                                 │
│  Source Register: Provenance tracked for each document                          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Summary

```
1. Student sends query
       │
       ▼
2. Flask app receives query
       │
       ▼
3. Extract intent (policy_qa, timetable, case_status, etc.)
       │
       ├─── If policy_qa ──► RAG RETRIEVAL
       │                        │
       │                        ▼
       │                   Retrieve relevant chunks
       │                        │
       │                        ▼
       │                   Inject context into prompt
       │                        │
       │                        ▼
       │                   Gemini generates grounded answer
       │                        │
       │                        ▼
       │                   Add source citations [Source: DOC-xx]
       │
       ├─── If timetable ──► Deterministic lookup (data/timetable.json)
       │
       ├─── If case_status ──► Deterministic lookup (data/cases.json)
       │
       └─── If out_of_scope ──► Refuse + redirect to human
              │
              ▼
4. Return response to student
```

---

## Response Format (with Sources)

```json
{
  "intent": "policy_qa",
  "answer": "According to the Academic Regulations (Regulation 4.2.1), students who fail a course may retake it under the following conditions: [details]. The retake fee is [amount]. [Source: DOC-01 Academic Regulations, Section 4.2]",
  "suggested_category": null,
  "needs_human": false,
  "redirect_office": null,
  "sources": ["DOC-01", "DOC-03"]
}
```

---

## Integration Points in app.py

```python
# In handle_message():
def handle_message(msg, session):
    # ... existing code ...
    
    # NEW: RAG retrieval for policy questions
    if intent == "policy_qa":
        context = retrieve_context(msg)  # Oscar's function
        system_prompt = inject_context(base_prompt, context)
        response = call_gemini(system_prompt, msg)
        response["sources"] = extract_sources(context)
    
    # ... rest of existing code ...
```
