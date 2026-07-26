# 06 — Submission

What you deliver, how to produce it, and how to check it. (Forking and the schedule live
elsewhere — see [`01_overview.md`](01_overview.md) for the fork, [`02_timeline.md`](02_timeline.md)
for the deadlines.)

## Deliverables

Everything lives in **your fork**:

| What | Where | Feeds |
|---|---|---|
| Team details | `submission/team.json` | — |
| 9 answers | `submission/level-1/q1..q3`, `level-2/q4..q6`, `level-3/q7..q9` | Answer accuracy |
| Your code | `app/` (and anything you added) | Implementation, Rigor, Integrity |
| Your document | `data/in/*.pdf` (committed) | grounding checks |
| Technical note | `TECHNICAL_NOTE.md` | Rigor |
| Presentation | to the jury on Friday | Jury (50%) |

Send us your **fork URL** (it's also in `submission/team.json`).

## How to produce the nine answers

You never hand-write the answer JSON — it comes out of your app.

1. **`team.json`** — fill in your team name, every member's name and email, and your repo URL.

2. **Ask your questions.** For each of your nine questions, call `POST /query` with the question
   and its level. Use Swagger (`/docs`), the Postman collection, or curl:

   ```bash
   curl -s localhost:8791/query -H 'content-type: application/json' \
     -d '{"question": "<your question>", "level": 1}'
   ```

   The system assigns the id and threads the conversation — you send only `question` and `level`
   (1, 2 or 3). Every answer is written to `data/out/` as a JSON file.

3. **Pick your best and copy them in.** When you're happy with an answer, copy the content of its
   `data/out/q_..._level_N_....json` file into the matching `submission/` file
   (`level-1/q1.json`, etc.). See [`../submission/README.md`](../submission/README.md).

## Validate before you push

Use the AI skill in [`../ai_skill/VALIDATE_SUBMISSION.md`](../ai_skill/VALIDATE_SUBMISSION.md) —
paste it into Claude Code (or Codex, Cursor, …). It checks your team details and nine answers are
filled in, your PDF is in `data/in/`, and your code has genuinely moved on from the skeleton (real
chunking, memory, retrieval). It only reads.

## Commit and push

```bash
git add submission/ data/in/ app/ TECHNICAL_NOTE.md
git commit -m "submission"
git push
```

Commit your **code** and your **document** too — the note's claims are checked against the code,
and your answers are checked against the PDF. You may keep committing until the Friday 12:00
deadline; the default branch at that moment is what we read.

## Common ways to lose points

- **Empty or malformed answer files** — `{}` or broken JSON scores 0. Copy a real `data/out/`
  answer in, and validate.
- **Paraphrasing the evidence quote** — grounding is checked against your PDF; copy quotes exactly.
- **Forgetting to commit `data/in/`** — without your document we can't confirm your answers.
- **Skeleton code** — answers from the untouched baseline score poorly on the implementation and
  integrity criteria (see [`rubric.md`](rubric.md)).
