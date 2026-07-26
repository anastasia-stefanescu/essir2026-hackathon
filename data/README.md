# data/

Put the corpus PDF here. The challenge runs against **one** document.

```
data/
└── paper.pdf     ← the shared corpus (committed to the repo)
```

- The organisers ship the PDF in this folder — it is an **open-licensed** document,
  so it travels inside the repository and everyone works from the identical file.
- `POST /ingest` picks up the first `*.pdf` in this folder by default, or the exact
  `filename` you pass it.
- Page numbers everywhere mean the **PDF page**, 1-indexed from the first page of the
  file.

Do not swap the PDF for a different edition or a re-exported copy — your citations are
checked against this exact file, page by page.
