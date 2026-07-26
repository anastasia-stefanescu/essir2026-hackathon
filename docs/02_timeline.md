# 02 — Timeline

The hackathon runs across the week. These are the touchpoints that matter for your submission.

| When | What | What you do |
|---|---|---|
| **Monday** | You get the task | Fork the repo, get it running (`docker compose up`), **choose your document** and put it in `data/in/`. Read [`01_overview.md`](01_overview.md) and [`03_tasks.md`](03_tasks.md). |
| **Tuesday** | Questions | Ask the organisers anything about the task, rules or scoring. Or use the ready-made LLM advisor ([`08_advisor.md`](08_advisor.md)) — it helps with strategy and debugging (it can't see your document or give answers). |
| Wed–Thu | Build | Work through the three levels. Write your own nine questions about your document. |
| **Thursday** | Compliance submission | Push what you have and tell us — a **dress rehearsal, not graded**. Optionally run the validation skill first (see below) so we can confirm your submission is well-formed before the real deadline. |
| **Friday, 12:00** | **Final push deadline** | Commit and push everything — code, `submission/`, technical note. Whatever is on your default branch at 12:00 is what we evaluate. |
| **Friday** (after) | Presentation | Present and defend your system to the jury. |

## The validation skill (optional, recommended)

Before the Thursday and Friday pushes, check your submission is complete with the AI skill in
[`../ai_skill/VALIDATE_SUBMISSION.md`](../ai_skill/VALIDATE_SUBMISSION.md) — paste it into Claude
Code (or Codex, Cursor, …) and it verifies your team details and nine answers are filled in, your
PDF is in `data/in/`, and your code has moved on from the skeleton. It only reads; it changes
nothing.

## Deadlines, condensed

| What | When |
|---|---|
| Task released (fork + choose document) | Monday |
| Compliance submission (dress rehearsal) | Thursday |
| **Final git push** | **Friday, 12:00** |
| Presentation to the jury | Friday |

Git commit timestamps are authoritative. You can keep committing up to the deadline — see
[`06_submission.md`](06_submission.md).

## How it is scored

Final score = **50% code evaluation** (your repository) + **50% jury** (your presentation). The
criteria are in [`05_evaluation.md`](05_evaluation.md) and [`rubric.md`](rubric.md).
