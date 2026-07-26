# 06 — Submission

You deliver your **fork of this repository**, with your code, your nine answers, and your
technical note committed to it.

## Fork and clone

On GitHub, open this repository and click **Fork** (top right) to create a copy under your
own account or team org. Then:

```bash
git clone https://github.com/<your-team>/essir2026-aim-hackathon-participants.git
cd essir2026-aim-hackathon-participants
```

Build your system on the default branch (or merge into it before the deadline). We read the
default branch at deadline time.

> New to forking? A fork is your own server-side copy of the repo. You push to the fork, not
> to the original — you do not need write access to ours. GitHub's guide:
> <https://docs.github.com/get-started/quickstart/fork-a-repo>.

## Produce the nine answers

Run each question through your own running app and save the response:

```bash
# Level 1 — standalone
curl -s localhost:8000/query -H 'content-type: application/json' \
  -d '{"question_id":"q1","level":1,"question":"<question text>","conversation_id":"level-1"}' \
  > results/level-1/q1.json

# Level 2 — send q4,q5,q6 in order, SAME conversation_id, so memory carries across
for q in q4 q5 q6; do
  curl -s localhost:8000/query -H 'content-type: application/json' \
    -d "{\"question_id\":\"$q\",\"level\":2,\"question\":\"<...>\",\"conversation_id\":\"level-2\"}" \
    > results/level-2/$q.json
done
```

The `POST /query` response **is** the file format — save it verbatim. Layout and details in
[`../results/README.md`](../results/README.md).

## Commit and push

```bash
python tools/validate_results.py          # do this first
git add results/ TECHNICAL_NOTE.md app/
git commit -m "T07 submission"
git push origin main
```

Commit your **code** too — the technical note's claims are checked against it.

## Deliverables

| What | Where | Due |
|---|---|---|
| Compliance submission (dress rehearsal) | pushed to your fork | Thursday |
| Fork URL | sent to the organisers | Fri 12:00 |
| 9 answers | `results/level-N/qM.json` in your fork | Fri 12:00 |
| Technical note | `TECHNICAL_NOTE.md` in your fork | Fri 12:00 |
| Code | your fork | Fri 12:00 |
| Presentation | to the jury | Friday |

You may keep committing until the **Friday 12:00** deadline; the default branch at that moment is
what we read. A commit after the deadline is not counted. Do a compliance push on **Thursday** so
we can confirm your submission is well-formed before the real deadline.

## Optional

- **A UI** — build one on top of your API if you like. It does not change how the backend is
  graded, but it can help your presentation.
- **The Postman collection** in [`../postman/`](../postman/) — import it to drive the API by
  hand while developing.

## Common ways to lose points

- **Paraphrasing the evidence quote** — fuzzy matching forgives parser artefacts, not
  rewording. Caps the answer at 0.5.
- **Guessing the page** — ±2 is a small window. Emit it from your pipeline.
- **Empty or malformed answer files** — score 0. Run the validator.
- **Level-2 questions sent without a shared `conversation_id`** — your system has no history,
  and the follow-ups become unanswerable.
