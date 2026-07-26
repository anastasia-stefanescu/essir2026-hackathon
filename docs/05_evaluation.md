# 05 — Evaluation

How the score is put together. The full, binding criteria are in
[`rubric.md`](rubric.md) — read it; this page is the overview.

## Two halves, 50 / 50

| Component | Weight | What it is |
|---|---|---|
| **Code evaluation** | 50% | Your repository, assessed against the sixteen-criterion rubric — your answers, your implementation, your rigor, your integrity. |
| **Jury** | 50% | Your presentation, scored by the jury. |

```
final_score = 0.5 × code_score + 0.5 × jury_score
```

There is **no speed bonus** — submission time does not affect the score, as long as you push
before the Friday 12:00 deadline. What matters is what you built, not when you committed it.

## Code evaluation — 50%

Your repository is scored against sixteen criteria in four groups — **answer accuracy**,
**implementation**, **rigor** and **integrity** — each scored 0–100, weighted into a single code
score. **The criteria and their weights live in one place: [`rubric.md`](rubric.md).** Read it;
it is the authority, and this page won't repeat the numbers.

Two things there move the most marks, so they're worth internalising up front:

- **Grounding.** Every answer should carry a verbatim `evidence_quote` and its `page`. A quote
  that does not appear in the document counts against both the answer criteria and integrity — an
  ungrounded answer cannot be confirmed. Copy quotes exactly.
- **Build a real, general system.** Answers must come from your pipeline, not from code keyed to
  the specific nine questions. Hardcoding, question-specific hacks and fabricated evidence are
  penalised heavily under *Integrity*, and the technical note and presentation will expose them.

## Jury — 50%

Friday afternoon, you present and defend your system to the jury, who each give an overall mark
out of 100. They weigh:

| They look for | Strong | Weak |
|---|---|---|
| Technical substance | A real system you understand end to end | A chat product with the PDF attached |
| Design reasoning | You can defend a choice and name what it cost | Choices unexplained |
| Handling of failure | A diagnosed failure with evidence | "Everything worked" |
| Clarity | Structured, paced | Reads slides, overruns |
| Q&A | Answers what's asked, including "we don't know" | Deflects or invents |

At a doctoral school, understanding is weighted over polish. A modest system you can account for
beats a slick one you cannot.

## Deliverables that feed the score

| What | Feeds |
|---|---|
| Your code (in the fork) | Implementation, Rigor, Integrity |
| `submission/` — the nine answers | Answer accuracy |
| `TECHNICAL_NOTE.md` | Rigor (the technical-note criterion) |
| The presentation | The jury 50% |

See [`06_submission.md`](06_submission.md).

## Determinism and appeals

- Each answer is checked against your own document (the PDF in `data/in/`); each criterion score
  is anchored to concrete evidence in your repo, recorded in the feedback you receive.
- You may query a score within **30 minutes** of results with `(team, criterion, reasoning)`. The
  content of the document and the jury's marks are not appealable.
