# 02 — Timeline

The hackathon runs across the week. These are the touchpoints that matter for your submission.

## Monday — you get the task

The challenge opens. You receive the scaffold repository, the corpus PDF and the nine questions.
Fork the repo, get it running (`docker compose up`), and split the work across your team. Start
with [`01_overview.md`](01_overview.md) and [`03_tasks.md`](03_tasks.md).

## Tuesday — questions

Bring questions about the task, the rules or the scoring to the organisers. At any point you can
also use the ready-made strategy advisor we prepared — paste it into your own LLM and it will
help you plan and debug: [`08_advisor.md`](08_advisor.md). (The advisor never sees the document
and cannot give you answers; it is for strategy and engineering.)

## Thursday — compliance submission

Push what you have so far and tell us. This is a **dress rehearsal, not graded**: we confirm your
submission is well-formed — the repo is forked correctly, your `results/` are in the right shape,
and the validator passes:

```bash
python tools/validate_results.py
git add . && git commit -m "compliance submission" && git push
```

Getting this right on Thursday means Friday is just your final push, with no surprises.

## Friday — final push by 12:00

**Push your latest changes to git by 12:00.** That is the deadline. Whatever is on your default
branch at 12:00 is what we evaluate — code, `results/`, and your technical note.

```bash
python tools/validate_results.py        # last check
git add . && git commit -m "final submission" && git push
```

Later on Friday you **present and defend your system to the jury**.

## Deadlines, condensed

| What | When |
|---|---|
| Task released (fork, PDF, questions) | Monday |
| Compliance submission (dress rehearsal) | Thursday |
| **Final git push** | **Friday, 12:00** |
| Presentation to the jury | Friday |

Git commit timestamps are authoritative. You can keep committing up to the deadline — see
[`06_submission.md`](06_submission.md).

## How it is scored

Final score = **50% code evaluation** (your repository) + **50% jury** (your presentation). The
criteria are in [`05_evaluation.md`](05_evaluation.md) and [`rubric.md`](rubric.md).
