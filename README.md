# The Fourth Turn

A hackathon at **[ESSIR 2026](https://2026.essir.eu/)** — the European Summer School in
Information Retrieval, Bucharest, 27–31 July 2026. Over the week, in teams, you build a backend
that **answers questions about a large PDF through a conversation** — and this repository is
the scaffold you fork and build on.

## Why "The Fourth Turn"

A question-answering system is easy to show off on a single, self-contained question and hard
to sustain across a conversation. The first turn of a dialogue stands on its own. Each later
turn leans on what was already asked and answered — so by the time a user reaches, say, the
fourth turn — *"and how does that compare to the previous method?"* — the question can only be
understood in light of the turns before it. It has almost no meaning, and almost nothing to
search for, on its own.

The challenge is built around that progression, in three levels:

1. **Retrieval** — answer a self-contained question, grounded in the document.
2. **Conversational memory** — answer a follow-up that depends on earlier turns.
3. **Whole-document reasoning** — answer questions no single passage contains.

The name marks the point where plain retrieval stops being enough and *context engineering*
begins. That is the interesting part of building an assistant over a document, and it is what
this hackathon is about.

## What you do

- **Fork this repository** and build your system inside it. It already runs — a naive baseline
  that ingests the PDF, retrieves, and answers — and you improve it up the three levels.
- **Answer nine questions** (three per level) through your own `POST /query` endpoint and save
  each response as `results/level-N/qM.json`.
- **Deliver** your fork's URL, the nine answers, a two-page technical note, and a Friday
  presentation.

## The stack

Python · FastAPI · `uv` · Docker · Qdrant. Backend only (a frontend is optional). The LLM side
works with **Ollama**, **LM Studio**, or any hosted API via **litellm** — run it fully local
with no API keys if you like.

## Quick start

```bash
# 1. Fork on GitHub, then clone your fork
git clone https://github.com/<your-team>/essir2026-aim-hackathon-participants.git
cd essir2026-aim-hackathon-participants

# 2. Configure (choose your LLM provider and models)
cp .env.example .env      # then edit .env

# 3. Bring up the app + Qdrant
docker compose up --build
#    app     -> http://localhost:8000      (Swagger UI at /docs)
#    qdrant  -> http://localhost:6333

# 4. Index the PDF sitting in data/, then ask a question
curl -s localhost:8000/ingest -H 'content-type: application/json' -d '{}'
curl -s localhost:8000/query  -H 'content-type: application/json' \
  -d '{"question_id":"q1","level":1,"question":"What is this document about?","conversation_id":"level-1"}'
```

Prefer to run it without Docker?

```bash
uv sync
uv run uvicorn app.main:app --reload      # needs a reachable Qdrant + LLM
```

## Where things are

```
app/                 the FastAPI service you build on
├── main.py          app factory + Swagger
├── config.py        settings (.env)
├── models.py        request/response schemas — QueryResponse IS the graded format
├── llm/             Ollama · LM Studio · litellm interfaces (+ how to add your own)
├── vectorstore/     Qdrant wrapper (list / read / write)
├── rag/             chunk · ingest · retrieve · memory · pipeline  <- the challenge lives here
└── routes/          /health · /collections · /ingest · /query
data/                the corpus PDF (committed)
results/             your nine answers — the deliverable  (level-1/ level-2/ level-3/)
questions/           the nine questions
templates/           the answer format + the technical-note scaffold
postman/             a Postman/Bruno collection to drive the API by hand
tools/               validate_results.py — run before you push
docs/                everything below, in depth
```

Everywhere worth improving is marked with a `TODO(level-N)` comment pointing at the level it
unlocks. Start in `app/rag/`.

## Read next (`docs/`)

1. [`01_overview.md`](docs/01_overview.md) — what you are building and why it is complex.
2. [`02_timeline.md`](docs/02_timeline.md) — the week and every deadline.
3. [`03_tasks.md`](docs/03_tasks.md) — the three levels, and where each lives in the code.
4. [`04_rules.md`](docs/04_rules.md) — what is allowed, how teams work.
5. [`05_evaluation.md`](docs/05_evaluation.md) — how the score is put together (50% your
   repository + 50% the jury).
6. [`rubric.md`](docs/rubric.md) — the exact criteria your repository is assessed against.
7. [`06_submission.md`](docs/06_submission.md) — forking, and delivering your answers.
8. [`07_hints.md`](docs/07_hints.md) — where the time actually goes.
9. [`08_advisor.md`](docs/08_advisor.md) — a ready-to-paste prompt that turns your favorite LLM
   into a strategy advisor for this challenge.
10. [`09_faq.md`](docs/09_faq.md) — common questions.

## Before you push

```bash
python tools/validate_results.py
```

An empty or malformed answer file scores 0 for that question — this takes two seconds.
