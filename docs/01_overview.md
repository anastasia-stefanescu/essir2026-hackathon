# 01 — Overview

## What you are building

A backend service that answers questions about **a document you choose**, grounded in that
document and served over HTTP. You **fork this repository and build inside it**: it already runs
— a naive baseline that ingests a PDF, embeds it into Qdrant, retrieves, and answers — and your
job is to make it good enough to handle three rising levels of difficulty.

**Getting started:** fork the repo, `cp .env.example .env`, pick one open-access PDF you find
interesting and drop it in `data/in/`, then `docker compose up`. The [root README](../README.md)
has the exact steps. You also **write your own nine questions** about your document — three per
level (see [`../questions/questions.md`](../questions/questions.md)).

Python, FastAPI, `uv`, Docker, Qdrant. Backend only; no frontend is required (though you may add
one). It is an open-source challenge — any locally hostable model is fair. What to build is in
[`03_tasks.md`](03_tasks.md).

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

You work with a real, published PDF — not a clean synthetic one. Real layout (two columns,
tables, footnotes, math, a bibliography that looks like content to a naive chunker) means
extraction quality is a genuine part of the problem, and often the first thing that quietly
breaks a pipeline. Pick something substantial — the more it stretches your retrieval, the more
your system has to show.

## The scale is deliberate

One document, tens of pages. Large enough that dumping the whole thing into a prompt is
wasteful and attribution-poor, small enough that a well-built pipeline runs in seconds on a
laptop and you can check answers by hand. You are **not** being asked to build ingestion for
thousands of documents — that is a different problem. Here the document is fixed once you choose
it, and the difficulty is in the conversation, the grounding, and the whole-document reasoning.
The better your system reasons over your one document, the better it does.

## What you deliver

1. **Your fork's URL** — with your code and your `submission/`.
2. **Nine answers** — `submission/level-N/qM.json`, produced by your own `POST /query`.
3. **A two-page technical note** — [`../templates/technical-note.md`](../templates/technical-note.md).
4. **A presentation** on Friday.

Details in [`06_submission.md`](06_submission.md).

## What a good solution looks like

There's no single right architecture, and we don't want one — the chunking, the retrieval, the
memory, the model you pick, how you trade accuracy against cost: all of that is yours to decide,
and yours to explain on Friday.

If it helps, the teams who tend to do well share two habits. First, they **sort out the
follow-up before they search** — they turn *"and how big is it?"* into a real, standalone query
instead of embedding it as-is. Second, they **actually measure their own system** — they try a
change, look at whether it helped, and can tell you the number — rather than saying "it works"
and hoping. Neither takes cleverness, just the discipline to look. More of this in
[`07_hints.md`](07_hints.md).
