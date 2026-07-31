# Technical Note — Team OnlyOne

## Document

`patient-metadata-detection.pdf` (medRxiv, April 2025): NLP methods for detecting patient metadata in SARS-CoV-2 genome sequencing articles, using BERT classifiers and LLM prompting.

---

## What we changed from the baseline

### 1. PDF extraction — Marker JSON renderer (`app/rag/ingest.py`)

The baseline used pypdf (one string per page). We switched to Marker's JSON renderer (`marker.renderers.json.JSONRenderer`), which outputs block-level structure with `block_type` and `page_id` per block.

**Why it matters:** The markdown renderer returns a single string with no page breaks — all chunks got `page=1`. The JSON renderer gives `page_id` natively per block, fixing page attribution. It also lets us skip noise blocks by type (`PageHeader`, `PageFooter`, `Picture`, `Diagram`) and attach tables and footnotes to their surrounding body chunk rather than indexing them as standalone vectors.

**Artefact:** Before this change, every source in query responses showed `"page": 1`. After, pages 1–19 are correctly attributed (verified by inspecting `_chunks_from_marker_json` output).

### 2. Chunking (`app/rag/ingest.py`, `app/rag/chunking.py`)

The baseline indexed one vector per page (~19 vectors). We moved to sliding-window chunking over Marker's block output (800 chars / 150 overlap), producing **69–73 chunks** depending on ingest run.

Section breadcrumbs (e.g. `[2. Methods] [2.2.2. Classification]`) are built from `section_hierarchy` block metadata and stored in the LLM context. Breadcrumbs are **not** embedded by default (`EMBED_BREADCRUMBS=false`) — we found that including them in the embedding vector caused irrelevant chunks to rank highly when their section title matched the query topic (e.g. an acknowledgements chunk with breadcrumb `[3.2.3. Error analysis]` appeared in error-related queries).

### 3. Hybrid search (`app/rag/sparse.py`, `app/vectorstore/qdrant_store.py`)

Dense retrieval alone misses keyword-exact matches. We added sparse retrieval via SPLADE (fastembed backend, `prithivida/Splade_PP_en_v1`). Qdrant stores named vectors `"dense"` + `"sparse"` per chunk; at query time, hybrid mode fetches top-K from each index independently and fuses with Reciprocal Rank Fusion (RRF).

**Controlled by** `SEARCH_MODE=hybrid` in `.env`. Switching modes requires a full re-ingest (collection schema changes).

### 4. Conversational memory — Level 2 (`app/rag/memory.py`, `app/rag/retrieve.py`)

**Query rewriting:** `rewrite_query()` sends the conversation history + current question to the LLM with a system prompt instructing it to produce a self-contained search query. The rewritten query is stored in memory (not the original), so future follow-ups have fully resolved context.

**Example:** `"Why does that happen?"` → `"Why was the study's evaluation limited to manually validated true positive articles?"` (observed in `diagnostics.rewritten_query`).

**Persistent memory:** Conversation history stored in Redis (`memory:level-N` key, 24h TTL), falling back to in-process dict when `REDIS_URL` is unset. Survives server restarts.

**Known failure mode:** When the server is restarted and Redis is cleared, the first follow-up has no history and `rewritten_query` is null — the model cannot resolve the reference. Observed during testing.

### 5. Verbatim citations (`app/rag/pipeline.py`)

The baseline truncated each chunk to 300 chars with `…` as the evidence quote — not verbatim, not precise. We replaced this:

Each retrieved chunk is split into sentences (splitting on `". "`, merging single-word fragments to avoid false splits on `"Fig."`, `"et al."`). Each sentence is embedded with the same encoder; the one with highest dot-product similarity to the query vector is selected as `evidence_quote`. The quote is verbatim by construction — it is a substring of the retrieved chunk text.

---

## Ablation

| Change | Observed effect |
|---|---|
| `EMBED_BREADCRUMBS=true` vs `false` | With breadcrumbs in the vector, an acknowledgements chunk (`"This work was supported by NIH..."`) scored 0.767 for error-related queries due to its `[3.2.3. Error analysis]` prefix. With `false`, content-only similarity drops it out of top-5. |
| Marker JSON vs pypdf | pypdf: all chunks `page=1`. Marker JSON: pages 1–19 correctly assigned. |
| Sentence-level citation vs 300-char truncation | Truncation produced `…`-terminated non-verbatim quotes. Sentence selection produces checkable verbatim spans (e.g. `"The primary limitation of this study is that our evaluation..."` maps exactly to page 16). |

---

## Reproducibility

```bash
# Local (requires Ollama + Qdrant)
uv sync
uv run uvicorn app.main:app --port 8791 --reload
curl -s localhost:8791/ingest -H 'content-type: application/json' -d '{"reset": true}'

# Docker (all services included)
docker compose up --build
curl -s localhost:8791/ingest -H 'content-type: application/json' -d '{"reset": true}'
```

`.env` is not committed; copy `.env.example` and set `LLM_PROVIDER=ollama`, `CHAT_MODEL=gemma4:e4b`.

---

## Known limitations

- Level-3 answers rely on single-shot retrieval (top-5 chunks). Whole-document questions that require combining evidence from distant sections (e.g. comparing Table 1 and Table 2 results) fail when the relevant chunks are not all in the top-5.
- Query rewriting quality depends on the local model. `gemma4:e4b` occasionally returns the original question unchanged for ambiguous follow-ups.
- Token usage not tracked (`tokens: null` in diagnostics).
