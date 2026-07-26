# 04 — Rules

## Teams

- Teams form at the Monday opening. Target size **3–5**.
- Each team gets a code — `T01`, `T02`, … — used for your `results/` and your submission.

## What you build

- A **Python backend** built on this scaffold. Keep it Python; keep the `POST /query`
  contract (that is what produces your `results/`). Everything inside is yours to replace.
- You **must** have your own logic somewhere real — chunking, retrieval, memory, or
  reasoning. Wiring an endpoint straight to a commercial "chat with PDF" product is not
  building a system; the *Integrity* criteria and the jury defence are designed to catch it
  (see [`rubric.md`](rubric.md)).
- A frontend is **optional**. Backend is what is graded.

## Tools and models — allowed

- **Any model, any provider**: hosted (via litellm) or local (Ollama, LM Studio). No cost cap;
  bring your own keys.
- **Any library, any technique**: rerankers, hybrid search, graph stores, agent frameworks.
- **Internet access** is allowed.
- **Coding assistants** (Claude Code, Copilot, Cursor, …) are encouraged. Say how you used
  them in your note.
- **Reading the PDF yourself** is fine and sensible — but nine questions across three levels
  are not all answerable by hand in the time, and your system has to produce the answers.

## The corpus

- One PDF, committed in [`../data/`](../data/). Everyone uses the identical file.
- Do not swap or re-export it — citations are checked against this exact file, page by page.

## Answers and grounding

- Every answer is produced by your running app and saved as `results/level-N/qM.json` — the
  raw `POST /query` response.
- Every answer should carry a **verbatim** supporting quote and its page. A quote that does not
  match the PDF means the answer cannot be confirmed and is capped — see
  [`05_evaluation.md`](05_evaluation.md).

## Submission

- Deliverable is your **fork's URL** plus the committed `results/` and technical note.
- You may keep committing until the deadline; the state of your default branch at the deadline
  is what we read. Git timestamps are authoritative.
- Validate before you push: `python tools/validate_results.py`. A malformed or empty answer
  file scores 0 for that question.

## Conduct

- **No sharing of answers between teams.** Discussing approaches, libraries and PDF-parsing
  misery in the corridor is encouraged; sharing answers is not.
- **Do not submit under another team's code.**
- The corpus and questions are the same for everyone — there is nothing to obtain early.

Deliberate breaches are grounds for exclusion from scoring. This is a summer school; the point
is what you learn.

## Questions

- **Technical / logistical** — ask the organisers any time.
- **Rule interpretation** — see [`09_faq.md`](09_faq.md).
- **Strategy** — yours to work out; use [`08_advisor.md`](08_advisor.md).
- **The content of the PDF** — we will not answer. That is the challenge.
