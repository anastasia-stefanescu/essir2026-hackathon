# 04 — Rules

## Teams

- Teams form at the Monday opening. Target size **3–5**.
- Each team gets a code — `T01`, `T02`, … — used for your `submission/` and your submission.

## What you build

- A **Python backend** built on this scaffold. Keep it Python; keep the `POST /query`
  contract (that is what produces your `submission/`). Everything inside is yours to replace.
- You **must** have your own logic somewhere real — chunking, retrieval, memory, or
  reasoning. Wiring an endpoint straight to a commercial "chat with PDF" product is not
  building a system; the *Integrity* criteria and the jury defence are designed to catch it
  (see [`rubric.md`](rubric.md)).
- A frontend is **optional**. Backend is what is graded.

## Tools and models — allowed

This is an **open-source competition**. The spirit is: build something you host and run yourself.

- **Any open-source model you can host on a PC** — via LM Studio, Ollama, or your own server.
  This is the intended path. Hosted APIs (through litellm) are allowed too, but the interesting,
  defensible entries run local models.
- **Any library, any technique**: rerankers, hybrid search, graph stores, agent frameworks.
- **Any open tool that helps** — don't reinvent the wheel (see [`07_hints.md`](07_hints.md)).
- **Internet access** is allowed.
- **Coding assistants** (Claude Code, Copilot, Cursor, …) are encouraged. Say how you used them
  in your note.
- **Reading the PDF yourself** is fine and sensible — but your system has to produce the answers.

## Your document

- **You choose your own** open-access PDF and commit it in [`../data/in/`](../data/in/) — one
  document per team. Pick something substantial (30+ pages is a good target).
- Keep the same file all week — your answers are checked against the exact PDF you committed,
  page by page. Don't swap or re-export it mid-way.

## Answers and grounding

- Every answer is produced by your running app and saved as `submission/level-N/qM.json` — the
  raw `POST /query` response.
- Every answer should carry a **verbatim** supporting quote and its page. A quote that does not
  match the PDF means the answer cannot be confirmed and is capped — see
  [`05_evaluation.md`](05_evaluation.md).

## Submission

- Deliverable is your **fork's URL** plus the committed `submission/` and technical note.
- You may keep committing until the deadline; the state of your default branch at the deadline
  is what we read. Git timestamps are authoritative.
- Validate before you push with the AI skill in
  [`../ai_skill/VALIDATE_SUBMISSION.md`](../ai_skill/VALIDATE_SUBMISSION.md). A malformed or empty
  answer file scores 0 for that question.

## Conduct

- **No sharing of answers between teams.** Discussing approaches, libraries and PDF-parsing
  misery in the corridor is encouraged; sharing answers is not.
- **Do not submit under another team's code.**
- Each team has its own document and its own questions — build your own thing.

Deliberate breaches are grounds for exclusion from scoring. This is a summer school; the point
is what you learn.

## Questions

- **Technical / logistical** — ask the organisers any time.
- **Rule interpretation** — see [`09_faq.md`](09_faq.md).
- **Strategy** — yours to work out; use [`08_advisor.md`](08_advisor.md).
- **The content of the PDF** — we will not answer. That is the challenge.
