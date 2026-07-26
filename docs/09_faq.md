# 09 — FAQ

## The corpus

**Is it a real document?**
Yes — a real, open-licensed PDF, committed in [`../data/`](../data/) so everyone works from the
identical file. Page numbers mean the PDF page, 1-indexed.

**Can I answer from a model that already read it, instead of retrieving?**
You can try, but every answer needs a verbatim quote and a page, which a model answering from
memory produces badly — and the Level-3 questions need evidence combined across the document.
You will need the retrieval pipeline either way.

**Can I use the arXiv/HTML version instead of the PDF?**
For building, sure. But your `sources` quotes are matched against the committed PDF at the
claimed page, so you need page-accurate spans from that file.

## The app

**Do I have to use this scaffold?**
Yes — build on the fork. Keep it Python and keep the `POST /query` response shape (that is your
`results/` format). Everything inside `app/` is yours to replace.

**Do I have to use Qdrant / Ollama / the given structure?**
Qdrant and the compose file are provided so you start in minutes; you may swap the store or the
provider if you prefer. The LLM interfaces (Ollama, LM Studio, litellm) are scaffolded — add
another by implementing the protocols in `app/llm/base.py`.

**Can I run fully local, no API keys?**
Yes. Use Ollama or LM Studio (`LLM_PROVIDER=ollama` or `lmstudio`) with a local chat model and a
local embedding model. No hosted keys needed.

**The app answers but the answer is poor / says the LLM is unavailable.**
The baseline degrades to returning retrieved context when no LLM is reachable — check
`GET /health/ready` and your provider settings in `.env`. Once a model is reachable, improving
the answer is the challenge (chunking, retrieval, prompting).

**Do I need a frontend?**
No. Backend only is graded. A UI is optional and can help your presentation.

## Answers and submission

**How do I submit?**
Fork, build, run the nine questions through your app, save `results/level-N/qM.json`, commit,
push, send us the fork URL. See [`06_submission.md`](06_submission.md).

**Can I keep editing after I push?**
Yes — we read your default branch at the deadline. A commit after the deadline is not counted.

**What makes an answer file invalid?**
Malformed JSON or an empty `answer`. Both score 0 for that question. Run
`python tools/validate_results.py` before pushing.

**How exact must the evidence quote be?**
Fuzzy-matched at ratio ≥ 0.85 after whitespace normalisation, page ±2. Parser artefacts
(hyphenation, ligatures, spacing) are forgiven; paraphrase is not.

**How do the Level-2 questions work?**
They are follow-ups. Send q4, q5, q6 in order with the same `conversation_id` (`level-2`) so
your system has the history. Sent standalone, the follow-ups have no retrievable content.

## Scoring

**Is there a speed bonus?**
No. Submission time does not affect the score.

**What if I only reach Level 1 and 2?**
You score normally on those six questions and 0 on the three Level-3 ones (and lower on the
Level-3 *implementation* criteria). A strong Level 1 + 2, a good note and a clear presentation is
a solid result. The final score is 50% code evaluation + 50% jury — see [`rubric.md`](rubric.md).

**How is grading kept fair?**
One deterministic judge call per answer at `temperature = 0`, a pinned model, an anchored
rubric, every call logged. Appeals re-run against the logged call.

## Conduct

**Can I talk to other teams?**
About approaches and libraries — yes. About answers — no.

**Can I ask organisers what the document says?**
No. Anything else, yes.
