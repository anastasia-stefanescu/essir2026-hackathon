# data/

Two folders:

```
data/
├── in/     ← put YOUR chosen PDF here. /ingest reads from it.
└── out/    ← every /query answer is written here automatically.
```

## `in/` — the document you choose

**You choose your own document.** Pick one open-access PDF — a paper, thesis, report or manual
you find interesting — put it in `data/in/`, and **commit it** so we can check your answers
against the exact file you used. One document per team.

- `POST /ingest` picks up the first `*.pdf` in `data/in/` (or the `filename` you pass).
- Page numbers everywhere mean the **PDF page**, 1-indexed from the first page.
- Keep the same file all week — your citations are checked against it, page by page.

## `out/` — your working answers

Every `POST /query` writes its full response to `data/out/` as
`q_<id>_level_<level>_<datetime>.json`. These are your working outputs; pick your best ones and
copy them into `submission/`. This folder is git-ignored — it is scratch, not the deliverable.
