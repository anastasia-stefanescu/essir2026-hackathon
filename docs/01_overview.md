# 01 — Overview

## What you are building

A backend service that answers questions about a single large PDF, grounded in the document
and served over HTTP. You **fork this repository and build inside it**: it already runs — a
naive baseline that ingests the PDF, embeds it into Qdrant, retrieves, and answers — and your
job is to make it good enough to handle three rising levels of difficulty.

Python, FastAPI, `uv`, Docker, Qdrant. Backend only; no frontend is required (though you may
add one). The scaffold and how to run it are described in the [root README](../README.md);
what to build is in [`03_tasks.md`](03_tasks.md).

## Why this problem is complex

### A question is easy in isolation and hard in a conversation

Answering one self-contained question over a document is close to a solved pattern: embed the
question, retrieve the nearest passage, generate an answer. The difficulty appears the moment
questions come in sequence. A follow-up like *"and how does that compare to the baseline?"*
carries almost no searchable content on its own — its meaning lives in the turns before it.
Deciding **where that context is resolved** — in the query before retrieval, in the prompt, or
not at all — is the first real engineering problem here.

### Grounding is what separates reading from plausible generation

A language model can produce a confident, fluent paragraph about a document it has only
partly absorbed. Producing the exact sentence that supports a specific claim, on the right
page, is much harder to fake. Requiring a verbatim supporting quote turns "sounds right" into
"is grounded", and it is what makes an answer checkable.

### Some answers are not in any single passage

The hardest questions cannot be answered by retrieving one chunk. They require combining a
number from a table with a statement in the text, or reasoning over the structure of the
whole document ("summarise each section"). A single embed-and-retrieve step does not expose
that structure; getting there needs retrieval that reasons — multiple queries, multiple hops,
sometimes a second index. This is where a retrieval pipeline becomes an *agentic* one.

### The document is real

The corpus is a real, published PDF — not a clean synthetic one. Real academic layout (two
columns, tables, footnotes, math, a bibliography that looks like content to a naive chunker)
means extraction quality is a genuine part of the problem, and often the first thing that
quietly breaks a pipeline.

## The scale is deliberate

One document, tens of pages. Large enough that dumping the whole thing into a prompt is
wasteful and attribution-poor, small enough that a well-built pipeline runs in seconds on a
laptop and you can check answers by hand. You are **not** being asked to build ingestion for
thousands of documents — that is a different problem. Here the corpus is fixed and the
difficulty is in the conversation, the grounding, and the whole-document reasoning. The better
your system scales its *reasoning* over this one document, the better it does.

## What you deliver

1. **Your fork's URL** — with your code and your `results/`.
2. **Nine answers** — `results/level-N/qM.json`, produced by your own `POST /query`.
3. **A two-page technical note** — [`../templates/technical-note.md`](../templates/technical-note.md).
4. **A presentation** on Friday.

Details in [`06_submission.md`](06_submission.md).

## The shape of a good solution

We do not prescribe an architecture. Chunking, retrieval, memory, model choice and the
accuracy/cost trade-off are yours to decide and yours to defend. Two things reliably separate
strong entries: they **resolve the follow-up before retrieving**, and they **measured their
own system** rather than asserting it works. See [`07_hints.md`](07_hints.md).
