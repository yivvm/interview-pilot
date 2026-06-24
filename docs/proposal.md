# InterviewPilot — Capstone Proposal

**A private, local AI assistant that helps job seekers sharpen their résumé and prepare for interviews — running entirely on the user's own machine.**

---

## 1. Problem

Job seekers face three recurring problems when applying:

1. **Their résumé has blind spots they can't see.** Strengths go unstated, weak bullets go unnoticed, and quantifiable wins are left vague ("led a team" instead of "led a team of 6").
2. **A generic résumé doesn't match a specific job.** Candidates rarely tailor bullets to a job description, so they miss keywords and under-sell relevant experience.
3. **Interview prep is unstructured.** People walk in without having rehearsed the questions a given role is likely to ask.

Existing AI tools that help with this are typically **cloud services that ingest your résumé** — a privacy concern — and many **fabricate impressive-sounding metrics**, which is actively dangerous advice for a job application.

## 2. Solution

**InterviewPilot** is a three-section web app, powered by a local open-source LLM, that takes a candidate from a raw résumé to interview-ready:

![User journey](user-journey.png)

- **Resume Review** — analyzes the résumé on its own merits (strengths, weaknesses, "stories to share" prompts) and offers an **AI coach chat** for specific, grounded rewrites.
- **JD Match** — compares the résumé to a pasted job description and returns a match score, skill gaps by severity, and tailored bullet rewrites.
- **Interview Prep** — generates likely interview questions with answer scaffolds anchored to the candidate's own experience.

![What it does](features.png)

## 3. What makes it different — built for trust

The project's central design principle is **trustworthy, private AI**:

![Built for trust](trust.png)

- **Grounded answers** — the model uses only what's in the résumé; if something isn't there, it says so instead of inventing experience.
- **No fabricated metrics** — when a metric isn't provided, the coach suggests it as an `[X]` / `[N]` placeholder and never invents a statistic. (Enforced in the review chat, JD Match, and Interview Prep prompts.)
- **Runs 100% locally** — the model runs on the user's machine via Ollama; the résumé never leaves the device.
- **No paid APIs, no model training** — built on an open-source LLM; no external API calls, and no user data is used for training.

## 4. Architecture

Two apps over HTTP, with a local LLM and a SQLite cache — nothing leaves the machine:

![Architecture](architecture.png)

A résumé is uploaded, parsed to text (pypdf / python-docx), stored with the session in SQLite, fed into a prompt, sent to Ollama, and the JSON result is cached so repeat views are instant.

## 5. Tech stack

![Tech stack](tech-stack.png)

| Layer | Choice |
|---|---|
| Frontend | Streamlit (multipage) |
| Backend | FastAPI + uvicorn |
| Local AI | Ollama · `llama3.1:8b` |
| Data & parsing | SQLite (SQLAlchemy) · pypdf · python-docx |
| HTTP / config / tests | httpx · pydantic-settings · pytest |

## 6. Scope

**In scope (MVP, built):** résumé upload + parsing; the three analysis sections; an AI coach chat with in-memory chat history; per-session caching of results; a clean, themed UI; all running locally.

**Non-goals:** model training/fine-tuning; paid APIs; user accounts/authentication; multi-résumé management (one résumé per session); a vector DB / RAG (the résumé fits in the model's context).

## 7. Results

A working end-to-end application:
- All three sections function on real résumés (PDF and DOCX), returning structured, cached results.
- The Resume Review coach chat holds multi-turn context and produces grounded, placeholder-safe rewrites.
- The full pipeline runs offline on a laptop with an 8B model.

## 8. Future work

- Extend the chat coach to the JD Match and Interview Prep sections.
- Persist chat history to the database (currently in-memory per session).
- Side-by-side résumé diff (original vs. rewrite) and PDF export of interview prep.
- Streaming LLM responses for a faster feel.
- A test suite (parser, route happy-paths, prompt snapshots).

---

*See the [README](../README.md) for setup, the full API surface, and the database schema.*
