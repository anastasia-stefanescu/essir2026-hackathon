# 03 — Tasks: the three levels

You answer nine questions — three at each of three levels. The levels rise in difficulty and
map onto the three things a document assistant must do: **retrieve**, **remember**, and
**reason across the whole document**. They are cumulative: Level 2 assumes Level 1 works,
Level 3 assumes Level 2 works.

Build in order. A solid Level 1 is worth more than a broken Level 3.

Where each capability lives in the code is called out below — every improvement point in the
scaffold carries a matching `TODO(level-N)` comment.

---

## Level 1 — Retrieval (q1–q3)

**Goal**: answer a self-contained question and prove where the answer came from.

Each answer carries an `answer`, a verbatim `evidence_quote` from the PDF, and its `page`.
The baseline scaffold already does a rough version of this: parse the PDF, chunk it, embed it,
retrieve the nearest chunks, generate an answer. Your job is to make it *accurate* and its
citations *exact*.

**Where you work**: `app/rag/chunking.py` (chunk quality), `app/rag/ingest.py` (extraction),
`app/rag/pipeline.py` (turning a retrieved chunk into a precise citation).

**Where it breaks**: extraction on a real PDF is messy, and a bad chunk makes a correct
answer un-retrievable. If your quotes do not match the document, your citations fail — and a
failed citation means the answer cannot be confirmed.

---

## Level 2 — Conversational memory (q4–q6)

**Goal**: answer a follow-up that is meaningless without the conversation it belongs to.

This is the level the challenge is named for. The three questions form a short thread:

```
q4  What limitation do the authors acknowledge about their method?
q5  Why does that happen?                    <- "that" = the limitation from q4
q6  And how do they propose to address it?   <- no retrievable content on its own
```

Send q4, q5, q6 to `POST /query` with the **same `conversation_id`** (`level-2`), in order,
so your system has the history when the follow-up arrives.

The trap: embedding *"Why does that happen?"* as written retrieves noise — the string has no
searchable content. The fix is to **resolve the follow-up against the history into a
standalone query before retrieving it**, then search with that.

**Where you work**: `app/rag/retrieve.py::rewrite_query` (currently a no-op — this is the key
function), `app/rag/memory.py` (the conversation store), `app/rag/pipeline.py` (history in the
prompt). Note that history in the prompt is necessary but *not sufficient*: retrieval still
needs the rewritten query.

---

## Level 3 — Whole-document reasoning (q7–q9)

**Goal**: answer questions that no single passage contains.

These need evidence combined from distant parts of the document, or a view of its structure
that a flat vector search does not provide:

- combine a value in a **table** with a statement in the **text or references** elsewhere;
- **synthesise** across the document ("summarise the contribution of each section");
- **multi-hop** — chain two or three facts that appear pages apart.

The baseline will not answer these well, and that is intentional. Reaching them means
retrieval that *reasons*: multiple queries, iterative retrieve-reason-retrieve loops, a
second index (per-section summaries, or a graph of entities and references), or structure-aware
extraction that keeps tables intact. None of this is scaffolded — the `TODO(level-3)` comments
mark where it plugs in.

**Where you work**: `app/rag/retrieve.py` (multi-query, agentic retrieval),
`app/rag/pipeline.py` (a reasoning loop), and quite possibly new modules and a second store of
your own.

---

## Summary

| Level | Questions | You must | Fails when |
|---|---|---|---|
| 1 · Retrieve | q1–q3 | Answer + verbatim quote + page | Extraction mangles the text; citations don't match |
| 2 · Remember | q4–q6 | Resolve the follow-up against history before retrieving | *"Why does that happen?"* is embedded as written |
| 3 · Reason | q7–q9 | Combine evidence across the whole document | One chunk is retrieved for a question that needs many |

Now read [`05_evaluation.md`](05_evaluation.md) for how each is scored, and
[`07_hints.md`](07_hints.md) for where the time goes.
