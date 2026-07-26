# submission/ — your deliverable

This is what we grade. It holds your **team details** and your **nine chosen answers**.

```
submission/
├── team.json            who you are (fill this in)
├── level-1/  q1.json  q2.json  q3.json      Level 1 — retrieval
├── level-2/  q4.json  q5.json  q6.json      Level 2 — conversational memory
└── level-3/  q7.json  q8.json  q9.json      Level 3 — whole-document reasoning
```

The three levels match [`../docs/03_tasks.md`](../docs/03_tasks.md): q1–q3 are Level 1, q4–q6
Level 2, q7–q9 Level 3.

## How to fill it in

1. **`team.json`** — your team name, every member's name and email, and the URL of your repo.

2. **The nine answer files start empty (`{}`).** You do **not** hand-write them. Every time you
   call `POST /query`, the app saves the full answer to `data/out/`. When you are happy with an
   answer, **copy the content of that file from `data/out/` into the matching `submission/`
   file** and commit it.

   Example: you like the `data/out/q_ab12cd_level_1_20260731-094112.json` you produced for a
   Level-1 question → copy its content into `submission/level-1/q1.json`.

The answer format is whatever `POST /query` returns — see it live in Swagger (`/docs`) or the
Postman collection. You never write the JSON by hand.

## Before you push

Validate your submission with the AI skill in [`../ai_skill/`](../ai_skill/) — paste
`VALIDATE_SUBMISSION.md` into Claude Code (or Codex, Cursor, …) and it checks that your team
details and all nine answers are filled in, your PDF is in `data/in/`, and your code has moved
on from the skeleton. See [`../docs/06_submission.md`](../docs/06_submission.md).

**An empty or malformed answer file scores 0 for that question.**
