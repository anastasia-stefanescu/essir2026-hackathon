# 07 — Hints

Where the time goes, and the non-obvious calls. Every item here is load-bearing.

## 1. Feed the docs to your LLM

Every file here is written to be pasted. Give an LLM [`03_tasks.md`](03_tasks.md),
[`05_evaluation.md`](05_evaluation.md) and the [root README](../README.md) and ask it to
restate the levels, the scoring and the API. Then keep it as a coach with
[`08_advisor.md`](08_advisor.md).

## 2. Get the baseline running before you change anything

`docker compose up --build`, `POST /ingest`, `POST /query`. See the pipeline work end to end
first, then improve one stage at a time and re-run. A working baseline you can measure against
is worth more on Tuesday than a clever design you cannot yet run.

## 3. Extraction quality quietly decides Level 1

The single biggest early time sink, and the most common silent failure. `pypdf` (the default)
is fine on clean digital PDFs and poor on complex layout — two columns, tables, ligatures,
hyphenation across line breaks, footnotes mid-sentence. If your extracted text disagrees with
the document, your citations will not match and every answer is capped at 0.5.

Compare a couple of extractors on the real PDF before committing — PyMuPDF, pdfplumber,
Docling, GROBID and Marker all behave differently, and one will read your document best. Spend
an hour on this, not the whole day. Keep the page number with every chunk so emitting a correct
citation is free.

## 4. Do not embed the follow-up as written (Level 2)

`"Why does that happen?"` has no retrievable content. Embedding it returns noise. The fix is
`rewrite_query` in `app/rag/retrieve.py` — currently a no-op. Use a small LLM call to turn the
follow-up plus the recent turns into a standalone query, then retrieve with that. Leave
genuinely standalone questions unchanged.

Log the rewritten query. When a Level-2 answer is wrong you need to see whether it failed at
rewriting or at retrieval.

## 5. History in the prompt is necessary but not sufficient

Passing the whole conversation to the model helps it *understand* the follow-up, but retrieval
still runs on whatever query you embed. If you skip the rewrite and only stuff history into the
prompt, the model reasons well over the wrong retrieved passages. You need both.

## 6. Level 3 is a different problem — plan for it

Whole-document questions are not solved by a bigger `top_k`. They need retrieval that reasons:
multiple queries, a retrieve-reason-retrieve loop, a per-section summary index, or a graph of
entities and references. Structure-aware extraction (keeping tables and headings intact) pays
off most here. None of this is scaffolded — the `TODO(level-3)` comments show where it plugs
in. Decide your Level-3 approach on Wednesday, not Friday afternoon.

## 7. Cite precisely, not broadly

The baseline returns the whole retrieved chunk as a citation. That often matches, but a precise
supporting sentence is stronger and less likely to fail the page check. Trimming the chunk down
to the sentence that actually supports the answer is cheap and worth it.

## 8. Answer every question

An empty answer scores 0; a wrong answer scores 0 but costs nothing more. There is no penalty
for trying. Fill in all nine, even the Level-3 ones you are unsure of.

## 9. Measure your own system

Half the score is the jury defence, and within the code evaluation the rigor group (measurement,
the technical note) is a fifth of it. Run the questions, look at where they fail, do one ablation
("added query rewriting → fixed 2 of 3 Level-2 questions"), and write the number down. An honest
negative result scores above an unexamined claim. Start the note on Wednesday.

## A workable 12-hour plan

One way to spend the time; not required.

| Session | Focus |
|---|---|
| Monday | Read the docs. Fork, `docker compose up`, ingest, one query. Split extraction / retrieval / conversation. |
| Tuesday | **Level 1**: settle extraction, improve chunking, exact citations. Answer q1–q3. Bring questions to the organisers. |
| Tue evening | Add query rewriting. Re-run — your first ablation. |
| Wednesday | **Level 2**: memory + rewrite. Answer q4–q6. Decide the Level-3 approach. Start the note. |
| Thursday | **Level 3**: multi-hop / agentic retrieval / a second index. Answer q7–q9. **Compliance push** so we can check your submission is well-formed. |
| Fri before 12:00 | Validate, commit, final push. |
| Friday | Present to the jury. |
