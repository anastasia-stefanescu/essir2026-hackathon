---
name: validate-submission
description: Validate the hackathon submission for completeness and compliance before pushing
---

## What to check

Report each item as PASS / FAIL / WARN with a one-line reason, then a final verdict.

### 1. Team details — `submission/team.json`
- The file parses as JSON.
- `team_name` is non-empty.
- `members` is a non-empty list, and **every** member has a non-empty `name` and a
  plausible `email` (contains `@`).
- `repo_url` is a non-empty URL to this repository.

### 2. Answers — `submission/level-*/q*.json`
All nine files must be present: `level-1/q1..q3`, `level-2/q4..q6`, `level-3/q7..q9`.
For each file:
- It parses as JSON and is **not empty** (`{}` means you have not filled it in — FAIL).
- It has a non-empty `answer`.
- Its `level` matches the folder (q1–q3 → 1, q4–q6 → 2, q7–q9 → 3).
- It has at least one entry in `sources`, and each source has a `page` and a `quote`
  (an ungrounded answer cannot be confirmed — WARN if missing).
- It looks like a real `/query` response (has `question`, `question_id`, `diagnostics`),
  i.e. it was produced by the app and copied from `data/out/`, not typed by hand.

### 3. The document — `data/in/`
- There is exactly one `*.pdf` in `data/in/` (WARN if more than one; FAIL if none).
- It is committed to git (`git ls-files data/in` lists it), so the organisers get the exact
  file your answers were graded against.

### 4. The code has moved on from the skeleton
The scaffold ships a deliberately weak baseline. A compliant submission shows real work in the
retrieval pipeline. Check `app/rag/` and report what is still untouched:
- **Chunking** — `app/rag/chunking.py::chunk_pages` in the skeleton indexes one chunk per page.
  FAIL if it is unchanged (no chunking implemented).
- **Conversational memory (Level 2)** — `app/rag/retrieve.py::rewrite_query` in the skeleton is
  a no-op that returns the question unchanged. WARN if unchanged (Level 2 will score poorly).
- **Embeddings / retrieval** — note whether `app/rag/embeddings.py` or `retrieve.py` show any
  real changes from the default (a different model, a reranker, hybrid search, multi-query…).
- **Whole-document reasoning (Level 3)** — note whether there is anything beyond single-shot
  retrieval (agentic loop, second index, table handling).

A quick way to see divergence: `git diff --stat <first-commit> -- app/` (or compare against the
upstream template). Summarise which `TODO(level-N)` markers are still present untouched.

### 5. It runs
- `pyproject.toml`, `uv.lock`, `Dockerfile` and `docker-compose.yml` are present.
- `.env` is **not** committed (secrets) but `.env.example` is.
- Nothing obviously prevents `docker compose up --build` from working (missing files,
  syntax errors in `app/`).

---

## Output

Finish with a short table (item → PASS/FAIL/WARN) and a verdict:

- **READY** — all of §1–§3 pass and the code shows real work (§4).
- **NOT READY** — list exactly what to fix, most important first.

Be specific and honest — this is the same bar the organisers apply.
