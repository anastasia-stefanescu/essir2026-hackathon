# Solution — The Fourth Turn (ESSIR 2026)

Our RAG-over-PDF backend for the ESSIR 2026 hackathon. The system answers nine questions about a chosen PDF across three levels of difficulty: standalone retrieval (L1), conversational follow-ups (L2), and whole-document reasoning (L3).

## Document

**`patient-metadata-detection.pdf`** — placed in `data/in/`. This is the PDF the nine questions are written about and all answers are grounded in.

## Stack

| Layer | Choice | Why |
|---|---|---|
| LLM | Ollama + `gemma4:e4b` | Local, open-source, no API keys |
| Embeddings | `intfloat/multilingual-e5-large` via sentence-transformers | Strong multilingual baseline, runs locally |
| Vector store | Qdrant in embedded mode (`./data/qdrant`) | No Docker required for local dev |
| PDF extraction | PyMuPDF (`pymupdf`) | Cleaner text than pypdf on real-layout PDFs |
| Chunking | Sliding-window character chunking (800 chars / 150 overlap) | Better retrieval granularity than one vector per page |
| Framework | FastAPI + `uv` | As required by the scaffold |

## Architecture

```
PDF (data/in/)
  │
  ▼ extract_pages()  [PyMuPDF]
list[str]  — one string per page
  │
  ▼ chunk_pages()  [sliding window, 800 chars / 150 overlap]
list[Chunk]  — text + page + index
  │
  ▼ SentenceTransformerEmbedder.embed()  [multilingual-e5-large]
list[vector]
  │
  ▼ Qdrant (embedded, ./data/qdrant)
   collection: aim_hackathon
```

**Query path (`POST /query`):**

```
question + level
  │
  ▼ memory.get_history()  [in-process dict keyed by "level-N"]
  │
  ▼ rewrite_query()  [LLM rewrites follow-ups into standalone queries — L2]
  │
  ▼ embedder.embed(query)  →  store.search(vector, top_k=5)
list[Context]  — top-5 chunks with page, score, title
  │
  ▼ _sources_from()  [sentence-level scoring: pick best sentence per chunk]
list[Source]  — verbatim quote + page
  │
  ▼ _build_messages()  [system + history + context block + question]
  │
  ▼ OllamaClient.chat()  [gemma4:e4b]
answer_text
  │
  ▼ memory.append()  →  data/out/<id>_level_<N>_<stamp>.json
QueryResponse
```

## What we implemented at each level

### Level 1 — Retrieval

**Goal:** answer a self-contained question and cite the exact sentence.

- **Chunking:** replaced the one-vector-per-page baseline with a sliding-window chunker (`chunk_size=800`, `chunk_overlap=150`). This keeps chunks within the embedding model's effective window and retrieves finer-grained passages.
- **PDF extraction:** switched from `pypdf` to `pymupdf` (`PDF_READER=pymupdf` in `.env`). PyMuPDF handles columns, ligatures, and hyphenation more reliably.
- **Sentence-level quotes:** `_sources_from()` in `pipeline.py` splits each retrieved chunk into sentences, embeds them, and selects the single sentence with the highest cosine similarity to the query vector. This produces a precise, verbatim `quote` rather than exposing the whole chunk.

### Level 2 — Conversational memory

**Goal:** answer a follow-up that only makes sense given the earlier turns.

- **Query rewriting:** `rewrite_query()` in `retrieve.py` is fully implemented. When history exists, the LLM is prompted to rewrite the follow-up into a self-contained query before retrieval. Example: *"Why does that happen?"* → *"Why does [the limitation from the previous turn] happen?"*. The rewritten query appears in `diagnostics.rewritten_query` in the response.
- **Conversation threading:** all level-2 queries share `conversation_id = "level-2"`. History is stored in an in-process dict (`memory.py`); if `REDIS_URL` is set, it uses Redis for persistence across restarts.
- **History in the prompt:** the full conversation history is injected into the LLM messages before the current question, so the model also has context for generation (not just retrieval).

### Level 3 — Whole-document reasoning

**Goal:** answer questions that no single passage contains.

- **Structure-aware extraction (Marker):** `PDF_READER=marker` activates a Marker-based path in `ingest.py`. The JSON renderer preserves section hierarchy, and `_chunks_from_marker_json()` attaches breadcrumb titles (e.g. `[Methods] [2.2. Detection]`) to each chunk. This keeps chunks structurally located so the retriever can surface passages from the right section.
- **Breadcrumb embedding:** when `EMBED_BREADCRUMBS=true`, the section path is prepended to the embedded text. A question about a specific section then matches the correct breadcrumb-tagged chunks more reliably.
- **Table handling:** Marker's JSON renderer identifies table blocks; `_chunks_from_marker_json()` attaches them inline to the preceding body chunk rather than indexing them as orphan vectors, so a table value and its surrounding prose end up in the same chunk.
- **Note:** multi-query fan-out and agentic retrieve-reason-retrieve loops are not yet implemented. L3 benefits from the structural improvements above but does not yet do multiple retrieval passes.

## Configuration

Key settings in `.env`:

```
LLM_PROVIDER=ollama
CHAT_MODEL=gemma4:e4b
OLLAMA_BASE_URL=http://localhost:11434

EMBEDDING_BACKEND=sentence-transformers
EMBEDDING_MODEL=intfloat/multilingual-e5-large

QDRANT_LOCAL_PATH=./data/qdrant   # embedded Qdrant — no Docker needed
PDF_READER=pymupdf                # or "marker" for structure-aware L3 ingestion

CHUNK_SIZE=800
CHUNK_OVERLAP=150
TOP_K=5
```

## Running locally

```bash
# 1. Install dependencies
uv sync

# 2. Start Ollama with the model
ollama run gemma4:e4b

# 3. Start the server
uv run uvicorn app.main:app --port 8791 --reload

# 4. Index the PDF
curl -s localhost:8791/ingest -H 'content-type: application/json' -d '{}'

# 5. Ask a question
curl -s localhost:8791/query -H 'content-type: application/json' \
  -d '{"question": "What is the paper about?", "level": 1}'
```

Swagger UI: `http://localhost:8791/docs`  
Re-index (reset): add `"reset": true` to the `/ingest` body.

## Key design decisions

**Why PyMuPDF over pypdf?**  
Real PDFs have multi-column layouts, hyphenated words, and ligatures. PyMuPDF applies better heuristics for reading order and ligature resolution. The difference shows in citation matching: quotes from pypdf frequently contain artefacts that don't match the visual PDF text.

**Why sliding-window chunking over sentence chunking?**  
Sentence-boundary detection is fragile on extracted text (abbreviations, footnote markers, equations break it). Character windows with overlap are deterministic and predictable; the 150-char overlap preserves cross-boundary context. For the Marker path, paragraph-level splitting is structure-aware and more natural.

**Why query rewriting before embedding, not just history in the prompt?**  
History in the prompt helps the LLM generate a coherent answer, but it does not help retrieval. The embedding of *"Why does that happen?"* returns noise because the string has no searchable content. Rewriting it to a standalone query first is the only way to retrieve the correct passage.

**Why embedded Qdrant (local path) instead of Docker?**  
Fewer moving parts for local development. The `QDRANT_LOCAL_PATH=./data/qdrant` setting uses Qdrant's embedded mode — no Docker daemon required. For deployment or multi-worker use, switch back to the Docker path and set `QDRANT_URL`.

**Embedding model choice**  
`intfloat/multilingual-e5-large` supports asymmetric retrieval (the `query:` / `passage:` prefixes) and scores well on passage retrieval benchmarks. The multilingual capability is insurance if the document contains non-English passages (tables, references, captions).

## Trade-offs and limitations

- **L3 retrieval is single-pass.** Multi-query fan-out and agentic loops are not implemented. Questions that require combining evidence from three or more distant passages may receive incomplete answers.
- **In-process memory resets on restart.** Level-2 conversation history is lost if the server restarts between questions. Use `REDIS_URL` for persistence.
- **Marker is slow on first ingest.** The Marker PDF reader downloads ML models and runs them locally; ingestion takes minutes rather than seconds. PyMuPDF is used by default for speed.
- **Sentence splitting is heuristic.** The sentence scorer in `_sources_from()` splits on `". "` which breaks on abbreviations. This occasionally produces slightly over- or under-quoted citations.
