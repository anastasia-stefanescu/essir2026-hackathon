# 09 — FAQ

## Your document

**Which document do I use?**
One you choose yourself — any open-access PDF you find interesting. Put it in `data/in/` and
commit it. One document per team; page numbers mean the PDF page, 1-indexed.

**Can I answer from a model that already read my document, instead of retrieving?**
You can try, but every answer needs a verbatim quote and a page, which a model answering from
memory produces badly — and the Level-3 questions need evidence combined across the document. You
will need the retrieval pipeline either way.

**Can I use the arXiv/HTML version instead of the PDF?**
For building, sure. But your `sources` quotes are checked against the committed PDF at the claimed
page, so you need page-accurate spans from that file.

## Open-source

**Is this really open-source only?**
It's an open-source competition. The intended path is a model you host yourself — LM Studio,
Ollama, vLLM, your own server. Hosted APIs (via litellm) are allowed, but the strong, defensible
entries run local, open models. There's no cost cap, but there's also no need to spend anything.

**Should I just feed the whole document to a huge-context model and skip retrieval?**
No — and it's a trap. Pasting the entire document into a 1M-context model is expensive, slow, and
worst of all it's ungrounded: the model won't reliably tell you *which sentence on which page*
supports its answer, which is exactly what you're scored on. It also falls apart on the
whole-document Level-3 questions. Retrieval isn't a limitation to brute-force past; building it
well *is* the challenge. Use open tools, don't reinvent the wheel — see
[`07_hints.md`](07_hints.md).

## The app

**Do I have to use this scaffold?**
Yes — build on the fork. Keep it Python and keep the `POST /query` response shape (that is your
`submission/` format). Everything inside `app/` is yours to replace.

**Do I have to use Qdrant / LM Studio / the given structure?**
Qdrant and the compose file are provided so you start in minutes; swap the store or provider if
you prefer. The LLM interfaces (LM Studio, Ollama, litellm) are scaffolded — add another by
implementing the protocols in `app/llm/base.py`.

**Can I run fully local, no API keys?**
Yes — that's the default. LM Studio or Ollama for the chat model, and the embeddings run locally
out of the box (sentence-transformers, downloads once). No hosted keys needed.

**The app answers but the answer is poor / says the LLM is unavailable.**
The baseline degrades to returning retrieved context when no LLM is reachable — check
`GET /health/ready` and your provider settings in `.env`. Once a model is reachable, improving the
answer is the challenge (chunking, retrieval, prompting).

**Do I need a frontend?**
No. Backend only is graded. A UI is optional and can help your presentation.

## Answers and submission

**How do I submit?**
Fork, build, run your nine questions through your app (each answer is saved to `data/out/`), copy
your best into `submission/`, fill `submission/team.json`, commit and push. See
[`06_submission.md`](06_submission.md).

**Can I keep editing after I push?**
Yes — we read your default branch at the Friday 12:00 deadline. A commit after it is not counted.

**What makes an answer file invalid?**
Malformed JSON or an empty `answer`. Both score 0 for that question. Check with the skill in
[`../ai_skill/VALIDATE_SUBMISSION.md`](../ai_skill/VALIDATE_SUBMISSION.md) before pushing.

**How exact must the evidence quote be?**
It should be text that actually appears on the cited page. Small differences from PDF extraction
(hyphenation, spacing, ligatures) are fine; a paraphrase that isn't in the document is not — an
ungrounded answer can't be confirmed.

**How do the Level-2 questions work?**
They're follow-ups. Send your three level-2 questions in order at `level: 2`. The system threads
them into one conversation automatically (you don't pass any id), so your system can use the
earlier turns. Sent as isolated questions, the follow-ups have no retrievable content.

## Scoring

**Is there a speed bonus?**
No. Submission time does not affect the score, as long as you push before Friday 12:00.

**What if I only reach Level 1 and 2?**
You score normally on those six questions and 0 on the three Level-3 ones (and lower on the
Level-3 *implementation* criteria). A strong Level 1 + 2, a good note and a clear presentation is
a solid result. Final score = 50% code evaluation + 50% jury — see [`rubric.md`](rubric.md).

**How is grading kept fair?**
Every repository is assessed against the same published rubric ([`rubric.md`](rubric.md)), each
score anchored to concrete evidence in your repo and written up in the feedback you receive. You
can query a score within 30 minutes of results.

## Conduct

**Can I talk to other teams?**
About approaches and libraries — yes. About answers — no.

**Can I ask organisers what my document says?**
No — that part's on you. Anything about the task, rules or tooling, ask any time.
