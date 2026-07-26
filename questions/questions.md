# The nine questions

Nine questions, three per level. You run each through your `POST /query` endpoint and
save the response into the matching `results/level-N/qM.json`.

> **Released at the opening session**, once the corpus PDF is fixed. Until then the exact
> wording below is a placeholder that shows the *shape* of each level. What each level
> demands of your system does not change.

The three levels rise in difficulty and map onto the three things a document assistant has
to do — retrieve, remember, and reason across the whole document. See
[`../docs/03_tasks.md`](../docs/03_tasks.md).

---

## Level 1 — Retrieval (q1–q3) · `conversation_id: level-1`

Self-contained factual questions. Each answer sits in a single passage; find the right
chunk, ground the answer in it, cite the page.

- **q1** — *(placeholder)* A direct fact stated once in the document. e.g. "What dataset do
  the authors evaluate their method on?"
- **q2** — *(placeholder)* A fact stated in different words than the question uses (a
  paraphrase, so keyword search alone is weaker than semantic search).
- **q3** — *(placeholder)* A specific value that lives in a sentence, e.g. "What learning
  rate did the authors use for the final model?"

## Level 2 — Conversational memory (q4–q6) · `conversation_id: level-2`

Follow-up questions. Each depends on an earlier turn and is meaningless on its own. **Send
q4, q5, q6 in order, all with `conversation_id: level-2`**, so your system carries the
context forward.

- **q4** — *(placeholder)* Opens a topic. e.g. "What is the main limitation the authors
  acknowledge?"
- **q5** — *(placeholder)* A follow-up using a pronoun. e.g. "Why does **that** happen?" —
  "that" refers to the limitation from q4.
- **q6** — *(placeholder)* An elliptical follow-up. e.g. "And how do they propose to fix
  **it**?" — no retrievable content without the previous two turns.

## Level 3 — Whole-document reasoning (q7–q9) · `conversation_id: level-3`

Questions no single chunk answers. They need evidence combined from distant parts of the
document, or a structure a flat vector search does not expose. The baseline scaffold will
not answer these well — this is where you build (agentic retrieval, multi-hop, a second
index; see the `TODO(level-3)` markers in `app/rag/`).

- **q7** — *(placeholder)* Combine a value from a **table** with a claim from the **running
  text or a reference** elsewhere in the document. e.g. "How does the result in Table 3
  compare with the baseline cited in the related-work section?"
- **q8** — *(placeholder)* Synthesise across the whole document. e.g. "Summarise the
  contribution of each section in one sentence."
- **q9** — *(placeholder)* A multi-hop question chaining two or three facts that appear
  pages apart. e.g. "Which of the datasets introduced in Section 2 is also used in the
  ablation, and what changed?"

---

### How to run them

```bash
# Level 1 — independent
curl -s localhost:8000/query -H 'content-type: application/json' \
  -d '{"question_id":"q1","level":1,"question":"...","conversation_id":"level-1"}' \
  > results/level-1/q1.json

# Level 2 — in order, shared conversation
for q in q4 q5 q6; do
  curl -s localhost:8000/query -H 'content-type: application/json' \
    -d "{\"question_id\":\"$q\",\"level\":2,\"question\":\"...\",\"conversation_id\":\"level-2\"}" \
    > results/level-2/$q.json
done
```

Then validate:

```bash
python tools/validate_results.py
```
