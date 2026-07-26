# results/ — your deliverable

This is what we grade. Nine answers, three per level, one JSON file each.

```
results/
├── level-1/  q1.json  q2.json  q3.json
├── level-2/  q4.json  q5.json  q6.json
└── level-3/  q7.json  q8.json  q9.json
```

The files are pre-created and empty. To fill one in:

1. Send the question to your running app:

   ```bash
   curl -s http://localhost:8000/query \
     -H "content-type: application/json" \
     -d '{"question_id":"q1","level":1,"question":"<the question text>","conversation_id":"level-1"}' \
     > results/level-1/q1.json
   ```

2. That's it — the `POST /query` response **is** the file format. Paste or pipe the
   response straight into the matching `qN.json`.

### Level 2 — send follow-ups in the same conversation

Level-2 questions build on an earlier question. Send every question of a level with the
**same `conversation_id`** (`level-2`), in order, so your system has the history when the
follow-up arrives. The pre-filled files already carry the right `conversation_id`.

### Before you push

```bash
python tools/validate_results.py
```

Checks all nine files parse, are in the right folders, and are filled in. A malformed or
empty file scores zero for that question.

### What each field is

See [`../templates/answer.example.json`](../templates/answer.example.json) and the
`QueryResponse` schema in [`../app/models.py`](../app/models.py). The graded fields are
`answer` and `sources` (a wrong or missing `sources` quote means we cannot confirm the
answer is grounded — see [`../docs/05_evaluation.md`](../docs/05_evaluation.md)).
