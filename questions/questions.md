# Your nine questions

You answer **nine questions about the document you chose** — three at each level. **You write
them yourself.** The examples below are *recommendations*: they show the kind and difficulty of
question each level is looking for. **Do not reuse them** — they won't fit your document. Craft
nine similar-in-spirit questions about your own PDF. Choosing good questions is part of the task,
and how well they fit the levels is graded (see *level-appropriate approach* in
[`../docs/rubric.md`](../docs/rubric.md)).

The three levels are explained in [`../docs/03_tasks.md`](../docs/03_tasks.md).

---

## Level 1 — Retrieval (q1–q3)

Self-contained factual questions, each answerable from a single passage.

*Recommendations (write your own equivalents about your document):*
- A direct fact stated once — e.g. *"What dataset do the authors evaluate on?"*
- A fact stated in different words than the question (semantic, not keyword) — e.g. *"Which
  benchmark measures the method's speed?"*
- A specific value in a sentence — e.g. *"What learning rate did they use?"*

## Level 2 — Conversational memory (q4–q6)

Follow-ups that only make sense given the earlier turns. Send them in order at `level: 2` — the
system threads them into one conversation automatically, so your system can use the history.

*Recommendations:*
- Open a topic — e.g. *"What is the main limitation the authors acknowledge?"*
- A pronoun follow-up — e.g. *"Why does **that** happen?"*
- An elliptical follow-up — e.g. *"And how do they propose to fix **it**?"*

## Level 3 — Whole-document reasoning (q7–q9)

Questions no single passage answers — evidence combined across the document.

*Recommendations:*
- Combine a **table** value with a claim in the **text or references** elsewhere.
- **Synthesise** across the document — e.g. *"Summarise the contribution of each section."*
- **Multi-hop** — chain two or three facts that appear pages apart.

---

## How to run them

Ask each question through your running app — via **Swagger** (`http://localhost:8791/docs`), the
**Postman collection** in [`../postman/`](../postman/), or curl. You send only the question and its
level:

```bash
# Level 1 — standalone
curl -s localhost:8791/query -H 'content-type: application/json' \
  -d '{"question": "<your level-1 question>", "level": 1}'

# Level 2 — send your three in order at level 2; they share one conversation automatically
curl -s localhost:8791/query -H 'content-type: application/json' \
  -d '{"question": "<your level-2 follow-up>", "level": 2}'
```

Each response is saved to `data/out/`. Copy your best ones into `submission/` — see
[`../submission/README.md`](../submission/README.md).
