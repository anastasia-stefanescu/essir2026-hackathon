# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

**The Fourth Turn** — an ESSIR 2026 hackathon scaffold. The goal is to build a RAG-over-PDF backend that answers 9 questions about a chosen PDF at three levels of difficulty: standalone retrieval (L1), conversational follow-ups (L2), and whole-document reasoning (L3). The 9 answers go into `submission/` and are graded.

## Commands

```bash
# Install dependencies
uv sync

# Run the server locally (requires running Qdrant + LLM)
uv run uvicorn app.main:app --port 8791 --reload

# Run with Docker (includes Qdrant)
docker compose up --build

# Lint
uv run ruff check .
uv run ruff format .

# Index the PDF
curl -s localhost:8791/ingest -H 'content-type: application/json' -d '{}'

# Ask a question at a given level
curl -s localhost:8791/query -H 'content-type: application/json' \
  -d '{"question": "What is this paper about?", "level": 1}'

# Re-index (drop and recreate collection)
curl -s localhost:8791/ingest -H 'content-type: application/json' -d '{"reset": true}'
```

Swagger UI: `http://localhost:8791/docs`  
Qdrant dashboard: `http://localhost:6391/dashboard`

## Architecture

The RAG pipeline is: `PDF → extract_pages → chunk_pages → embed → Qdrant → retrieve → LLM → QueryResponse`

```
app/
├── main.py          FastAPI app factory; routes registered here
├── config.py        All settings via pydantic-settings; call get_settings() anywhere
├── models.py        QueryResponse IS the graded format — never change its shape
├── llm/
│   ├── base.py      ChatModel / EmbeddingModel protocols + Message TypedDict
│   ├── factory.py   get_client() — cached, dispatches on LLM_PROVIDER env var
│   ├── ollama.py    Ollama HTTP client
│   ├── lmstudio.py  LM Studio HTTP client
│   └── litellm_client.py  litellm wrapper for hosted APIs
├── rag/
│   ├── ingest.py    PDF extraction (pypdf / pymupdf / pdfplumber / marker), calls chunk_pages + embed + upsert
│   ├── chunking.py  chunk_pages() — currently passes through pages unchanged (TODO level-1)
│   ├── embeddings.py  get_embedder() — sentence-transformers (default) or provider
│   ├── retrieve.py  rewrite_query() (no-op, TODO level-2) + retrieve() → list[Context]
│   ├── memory.py    In-memory conversation store keyed by conversation_id
│   └── pipeline.py  answer() — the main entry point called by POST /query
└── vectorstore/
    └── qdrant_store.py  Thin wrapper: ensure_collection / upsert / search
```

**Request flow for POST /query**: `routes/query.py → pipeline.answer()` → get history from `memory` → `retrieve.rewrite_query()` (level 2) → `retrieve()` (embed query + Qdrant search) → `_build_messages()` → LLM chat → `memory.append()` → save to `data/out/` → return `QueryResponse`.

**Conversation threading**: all level-2 queries share `conversation_id = "level-2"`, level-1 shares `"level-1"`, etc. Memory is process-local and resets on restart.

**Settings** are read once and LRU-cached. To pick up a `.env` change while running with `--reload`, restart the process (the cache doesn't auto-invalidate).

## Where to improve (TODO markers)

Every improvement point has a `TODO(level-N)` comment in the code:

| File | What to do |
|------|-----------|
| `app/rag/chunking.py` | `chunk_pages()` — implement real chunking (L1). Currently one vector per page. |
| `app/rag/ingest.py` | `extract_pages()` — try pdfplumber / PyMuPDF / Marker for better extraction (L1). |
| `app/rag/pipeline.py` | `_sources_from()` — return precise sentence-level quotes, not the whole chunk (L1). |
| `app/rag/retrieve.py` | `rewrite_query()` — use LLM to resolve follow-ups into standalone queries (L2). |
| `app/rag/memory.py` | Persistent store if you need memory to survive restarts (L2 optional). |
| `app/rag/retrieve.py` | Multi-query / agentic retrieval for whole-document questions (L3). |
| `app/rag/pipeline.py` | Reasoning loop for L3 (retrieve → reason → retrieve again). |

## Submission

1. Place your chosen PDF in `data/in/`.
2. Run `/ingest` to index it.
3. Run `/query` for each of the 9 questions at the appropriate level.
4. Copy `data/out/<file>.json` content into the matching `submission/level-N/qN.json`.
5. Fill in `submission/team.json`.
6. Validate with `ai_skill/VALIDATE_SUBMISSION.md` before pushing.

The `QueryResponse` schema in `app/models.py` is the graded format — `answer`, `sources[].quote`, `sources[].page` are all checked. Quotes must be verbatim text from the PDF.

## LLM providers

Set `LLM_PROVIDER` in `.env` to one of: `ollama`, `lmstudio`, `litellm`.  
Default model: `gemma4:e4b` via Ollama. `CHAT_MODEL` must match what the provider serves.

To add a new provider: implement the `ChatModel` / `EmbeddingModel` protocols from `app/llm/base.py`, put it in a new module under `app/llm/`, and add a branch in `app/llm/factory.py`.

## Qdrant without Docker

Set `QDRANT_LOCAL_PATH=./data/qdrant` in `.env` to use an embedded (file-based) Qdrant — no Docker required.
