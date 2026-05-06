# InterviewPilot — Implementation Plan

**Capstone Project — CAP 942**
**Author:** Yiwen
**Repo:** `interview-pilot`
**Status:** MVP

> **InterviewPilot** is an AI-powered prep tool that helps candidates land interviews and perform once they're in the room. It sharpens your resume, tailors it to a specific job description, and generates likely interview questions with bullet-point answer scaffolds — all running locally on an open-source LLM.
>
> Naming note: "InterviewPilot" is part of a planned family of focused prep tools (future siblings could include `lsat-pilot`, `gre-pilot`, etc.). Each tool is laser-focused on one high-stakes preparation domain rather than sprawling into general career management.

---

## 1. Overview

A small, end-to-end AI application that helps job seekers improve their resume and prepare for interviews. The user uploads a resume, then progresses through three sections, each powered by an open-source LLM running locally via Ollama.

### What it does

1. **Upload** — User uploads a resume (PDF or DOCX).
2. **Section 1 — Resume Review (no JD):** LLM analyzes the resume on its own merits. Output: improvement comments + open-ended prompts that nudge the user to share more stories/accomplishments.
3. **Section 2 — JD-Targeted Match:** User pastes a job description. LLM returns a match percentage, gap analysis, and tailored rewrite suggestions.
4. **Section 3 — Interview Prep:** Using the same JD, LLM produces likely interview questions with **bullet-point answer scaffolds** drawn from the resume (not full paragraphs).

### Non-goals (MVP boundaries)

- No model training or fine-tuning.
- No paid APIs (uses local Ollama).
- No user accounts / authentication.
- No multi-resume management — one resume per session.
- No vector DB / RAG (resume is short enough to fit in context).

---

## 2. Architecture

Two separate apps, communicating over HTTP. SQLite stores sessions and analysis results so the user can refresh without losing work.

```
┌──────────────────────┐         HTTP/JSON         ┌──────────────────────┐
│   Streamlit (UI)     │  ───────────────────────► │   FastAPI (backend)  │
│   localhost:8501     │  ◄─────────────────────── │   localhost:8000     │
└──────────────────────┘                           └──────────┬───────────┘
                                                              │
                                            ┌─────────────────┼─────────────────┐
                                            ▼                 ▼                 ▼
                                      ┌──────────┐    ┌──────────────┐   ┌────────────┐
                                      │  SQLite  │    │  Ollama API  │   │  pypdf /   │
                                      │ sessions │    │ localhost:   │   │  python-   │
                                      │ + cache  │    │ 11434        │   │  docx      │
                                      └──────────┘    └──────────────┘   └────────────┘
```

### Workflow per section

```
Section 1:  resume_text              → prompt template → LLM → JSON comments
Section 2:  resume_text + jd_text    → prompt template → LLM → JSON {score, gaps, rewrites}
Section 3:  resume_text + jd_text    → prompt template → LLM → JSON [{question, bullets[]}]
```

---

## 3. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Streamlit | Fastest path to a clean multi-section UI; matches capstone-approved tools |
| Backend | FastAPI | Lightweight, async-friendly, automatic OpenAPI docs for grading/demo |
| Database | SQLite (via SQLAlchemy) | Zero setup, file-based, perfect for MVP |
| LLM Runtime | Ollama | Local, free, capstone-approved; runs Llama 3 / Mistral |
| Model | `llama3.1:8b` (primary), fallback `mistral:7b` | Balance of quality + speed on 16 GB RAM |
| LLM Orchestration | Direct `httpx` calls to Ollama, optional LangChain | Keep it simple; LangChain only if a chain emerges as useful |
| PDF parsing | `pypdf` | Approved tool, simple text extraction |
| DOCX parsing | `python-docx` | Standard library for .docx |
| HTTP client (Streamlit → FastAPI) | `httpx` or `requests` | Either works |
| Env management | `python-dotenv` | Standard practice |
| Testing | `pytest` | Already familiar |

---

## 4. Repository Structure

Following the Study Buddy pattern of separating backend and frontend into distinct folders (or distinct repos if desired). Recommended for MVP: **one repo, two folders**, so the demo and grading are simpler.

```
interview-pilot/
├── README.md                       # Setup + run instructions
├── implementation.md               # This file
├── docs/
│   ├── proposal.md                 # 1–2 page capstone proposal
│   ├── architecture.png            # Workflow diagram for presentation
│   └── demo-script.md              # Talking points for the 5–10 min demo
│
├── backend/
│   ├── pyproject.toml              # or requirements.txt
│   ├── .env.example                # OLLAMA_HOST, MODEL_NAME, DB_URL
│   ├── app/
│   │   ├── main.py                 # FastAPI app + router registration
│   │   ├── config.py               # Settings (pydantic-settings)
│   │   ├── db.py                   # SQLAlchemy engine + session
│   │   ├── models.py               # SQLAlchemy ORM: Session, Analysis
│   │   ├── schemas.py              # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── upload.py           # POST /upload (PDF/DOCX → text)
│   │   │   ├── review.py           # POST /review (Section 1)
│   │   │   ├── match.py            # POST /match (Section 2)
│   │   │   └── interview.py        # POST /interview (Section 3)
│   │   ├── services/
│   │   │   ├── parser.py           # extract_text_from_pdf/docx
│   │   │   ├── llm.py              # Ollama client, retry, JSON-mode helpers
│   │   │   └── prompts.py          # Prompt templates (one per section)
│   │   └── utils/
│   │       └── text.py             # Token counting, truncation helpers
│   └── tests/
│       ├── test_parser.py
│       ├── test_prompts.py         # Snapshot tests for prompt rendering
│       └── test_routes.py          # FastAPI TestClient happy-paths
│
└── frontend/
    ├── requirements.txt
    ├── .env.example                # BACKEND_URL=http://localhost:8000
    ├── streamlit_app.py            # Entry point; tab/page navigation
    ├── pages/
    │   ├── 1_Upload.py
    │   ├── 2_Resume_Review.py
    │   ├── 3_JD_Match.py
    │   └── 4_Interview_Prep.py
    └── lib/
        ├── api.py                  # Thin client wrapping backend HTTP calls
        └── ui.py                   # Reusable components (cards, score gauges)
```

> If you later want to split into separate repos like Study Buddy, the boundary is already clean: `backend/` and `frontend/` become independent repos with their own READMEs and CI.

---

## 5. Database Schema (SQLite)

Two tables. Keep it minimal — no migrations framework needed for MVP, just `Base.metadata.create_all()` on startup.

### `sessions`

| Column | Type | Notes |
|---|---|---|
| id | TEXT (UUID) | Primary key |
| created_at | DATETIME | `datetime.utcnow()` default |
| resume_filename | TEXT | Original upload name |
| resume_text | TEXT | Extracted plain text |
| jd_text | TEXT NULL | Pasted job description (set later) |

### `analyses`

| Column | Type | Notes |
|---|---|---|
| id | INTEGER | Primary key |
| session_id | TEXT | FK → sessions.id |
| kind | TEXT | `review` / `match` / `interview` |
| created_at | DATETIME | |
| payload_json | TEXT | The full LLM response (cached so re-renders are free) |
| model_name | TEXT | e.g. `llama3.1:8b` (useful for the writeup) |

Why cache results: LLM calls take 10–60s locally. Caching makes the demo snappy and lets the user toggle between sections without re-hitting the model.

---

## 6. API Surface

All endpoints return JSON. All accept/return `session_id` so state lives in the DB, not the client.

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/upload` | multipart file | `{ session_id, resume_preview }` |
| GET | `/sessions/{id}` | — | full session record |
| POST | `/review` | `{ session_id }` | `{ strengths[], weaknesses[], story_prompts[] }` |
| POST | `/match` | `{ session_id, jd_text }` | `{ match_score, matching_skills[], gaps[], rewrite_suggestions[] }` |
| POST | `/interview` | `{ session_id }` *(uses stored JD)* | `[{ question, category, answer_bullets[], resume_anchor }]` |
| GET | `/health` | — | `{ status, ollama_reachable, model }` |

### Example: Section 2 response shape

```json
{
  "match_score": 72,
  "matching_skills": ["Python", "FastAPI", "AWS Lambda"],
  "gaps": [
    {"skill": "Kubernetes", "severity": "high", "suggestion": "Add any container orchestration exposure, even hobby projects"},
    {"skill": "GraphQL", "severity": "low", "suggestion": "Mention if used in side work"}
  ],
  "rewrite_suggestions": [
    {"original": "Built APIs", "improved": "Designed and deployed 12 production REST APIs handling 50k req/day on AWS Lambda"}
  ]
}
```

Streamlit then renders the score as a gauge, gaps as colored chips, and rewrites as before/after side-by-side cards.

---

## 7. LLM Strategy

### Model selection

- Primary: `llama3.1:8b` — strong instruction-following, JSON output is reliable.
- Fallback: `mistral:7b` — lighter, useful if RAM is tight during the demo.
- Set via env var `MODEL_NAME`, switchable without code change.

### Calling Ollama

Use `httpx.AsyncClient` to hit `POST http://localhost:11434/api/chat` with `format: "json"` to force structured output. Wrap in a thin `LLMClient` class with:

- `chat(system, user, schema_hint) -> dict`
- 60s timeout, 1 retry on JSON parse failure (with a "respond with valid JSON only" reminder appended).
- Logs prompt tokens + latency to a file — useful data for the writeup's "Challenges" section.

### Prompt templates

One template per section, in `services/prompts.py` as plain strings with `.format()` placeholders. Each template:

1. Sets a clear role ("You are a senior career coach...").
2. Specifies the output JSON schema inline.
3. Shows one short example (1-shot) for tricky outputs (interview bullets especially).
4. Reminds the model: respond with **JSON only**, no prose.

**Section 3's bullet-point rule** goes in the prompt as an explicit constraint:
> "Each answer must be 3–5 short bullet points, each ≤ 20 words. Bullets are talking-point cues, not full sentences. Anchor each set of bullets to a specific role or project from the candidate's resume."

---

## 8. Frontend Flow (Streamlit)

Use Streamlit's native multi-page app feature. Sidebar shows current `session_id` + uploaded resume name so the user always knows where they are.

### Page 1 — Upload
- File uploader (PDF/DOCX, ≤ 2 MB).
- On submit, POST to `/upload`, store `session_id` in `st.session_state`.
- Show extracted text in a collapsed expander so the user can verify parsing worked.

### Page 2 — Resume Review
- Big "Analyze my resume" button → POST `/review`.
- Render three columns: ✅ Strengths, ⚠️ Weaknesses, 💡 Stories to share.
- "Stories to share" is the inspiration prompt list — questions like *"You mention 'led a team' — how big was the team and what was the measurable outcome?"*

### Page 3 — JD Match
- Textarea for JD paste.
- POST `/match`.
- Render: large match-score gauge (st.metric or a small custom SVG), matching-skills chips, gap list with severity colors, before/after rewrite cards.

### Page 4 — Interview Prep
- Requires JD from page 3 (read from session).
- POST `/interview`.
- Render each question as an expandable card. Inside: bullet list of talking points + a small grey footnote showing which resume item the bullets come from.
- "Copy bullets" button on each card.

---

## 9. Build Plan (Suggested Order)

This order gets to a demo-able state fastest, then layers polish.

### Milestone 1 — Skeleton (Day 1)
- Repo scaffold per Section 4.
- FastAPI app with `/health` endpoint that pings Ollama.
- Streamlit app with empty pages and sidebar.
- README with `make backend` / `make frontend` commands (or plain `uvicorn` / `streamlit run`).

### Milestone 2 — Upload + parsing (Day 2)
- `services/parser.py` for PDF and DOCX.
- `/upload` endpoint + session creation.
- Streamlit upload page.
- Manual test with 2–3 real resumes (your own + 1 from a public sample).

### Milestone 3 — Section 1 working end-to-end (Day 3)
- Prompt template, LLMClient, `/review` endpoint.
- Streamlit page 2 rendering the response.
- This is the "vertical slice" — once this works, sections 2 and 3 are mostly copy-paste.

### Milestone 4 — Sections 2 and 3 (Days 4–5)
- `/match` and `/interview` endpoints + Streamlit pages.
- Cache results in `analyses` table.

### Milestone 5 — Polish + docs (Day 6)
- Score gauge, severity chips, copy buttons.
- Workflow diagram (draw.io or Excalidraw, export PNG to `docs/`).
- Demo script.
- README with screenshots.

### Milestone 6 — Tests + buffer (Day 7)
- pytest for parser and route happy-paths.
- Snapshot test for one prompt to catch accidental regressions.
- Record a backup demo video in case Ollama misbehaves on presentation day.

---

## 10. Local Setup (for the README)

```bash
# 1. Install Ollama and pull a model
brew install ollama          # or download from ollama.com
ollama serve &               # runs at localhost:11434
ollama pull llama3.1:8b

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run streamlit_app.py
```

Open `http://localhost:8501`.

---

## 11. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Ollama returns malformed JSON | Use `format: "json"` parameter; retry once with stricter reminder; fall back to a default error response so UI doesn't crash |
| Resume parsing fails on weird PDFs | Show extracted text preview on upload page so user catches it early; add a "paste as text" alternative input |
| LLM latency makes demo feel slow | Cache results in DB; pre-run all three sections on your demo resume the morning of presentation |
| 16 GB RAM not enough for `llama3.1:8b` | Already have `mistral:7b` as fallback in env config |
| Hallucinated experience in interview answers | Prompt explicitly says "only use information from the provided resume"; manual spot-checks during testing |

---

## 12. What the Capstone Rubric Maps To

| Rubric item | Where it lives |
|---|---|
| Proposal (60 pts) | `docs/proposal.md` — written first, before coding |
| Functional app runs end-to-end (210 pts) | All three sections + upload, demoed live |
| Code readability + structure | Folder layout in Section 4, type hints, docstrings on every public function |
| Documentation + workflow diagram (30 pts) | `README.md`, `docs/architecture.png`, this file |
| Presentation | `docs/demo-script.md` + 5–10 min walkthrough |

---

## 13. Stretch Ideas (Only If Time Permits)

Listed so they're easy to drop in *or* leave out. None are required.

- **Side-by-side resume diff:** Show the user's original bullet vs. the LLM-rewritten version with `difflib` highlights.
- **Export interview prep to PDF:** Use `reportlab` so the user can take printed cheat-sheets to the interview.
- **Multiple resumes per session:** Add a `resumes` table with FK to sessions.
- **RAG over a "best resumes" corpus:** ChromaDB + sentence-transformers, retrieve example bullet-point styles. Only worth it if you want to demonstrate vector-DB skills for the rubric.
- **Streaming responses:** Use Ollama's streaming endpoint so the UI shows tokens as they arrive — feels faster.

---

## 14. Open Questions to Answer Before Coding

1. Will you run the demo on your own laptop or a school machine? Confirms RAM/model choice.
2. ~~Project name and repo structure~~ ✅ **Decided:** `interview-pilot`, single repo with `backend/` + `frontend/` folders.
3. Any specific resume formats your target users would upload that aren't PDF/DOCX? (e.g., LinkedIn export)
4. For the future `lsat-pilot` sibling project — do you want to design InterviewPilot's prompt/LLM-client layer in a way that can be lifted into other Pilot tools? (Small refactor up front, big payoff later. Recommended: yes — keep `services/llm.py` and `services/prompts.py` generic enough to copy-paste.)
