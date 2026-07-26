# Evaluation rubric

**Published to participants.** This is exactly what your submission is assessed against — the
same file ships in the participants repo. Nothing here is hidden.

Your final score has two halves, weighted **50 / 50**:

- **Code evaluation (50%)** — your repository, assessed against the sixteen criteria below.
- **Jury (50%)** — your presentation, scored by the jury.

## Code evaluation — the sixteen criteria

Each criterion is scored **0–100**; the weighted sum (weights sum to 100) is your **code score**.

| Score | Meaning |
|---|---|
| ~90 | Exceptional — clearly exceeds what the level asks |
| ~75 | Strong — meets it well, minor gaps |
| ~60 | Adequate — works, real weaknesses |
| ~40 | Weak — partially there, significant problems |
| ~20 | Poor — attempted but largely failing |
| 0 | Absent or non-functional |

### Answer accuracy — 30%

| Criterion | Weight | What it measures |
|---|---|---|
| Level 1 answers (q1–q3) | 8 | Correct, grounded answers; the evidence quote appears on the cited page. |
| Level 2 answers (q4–q6) | 10 | Follow-ups answered correctly using the conversation, not as standalone queries. |
| Level 3 answers (q7–q9) | 12 | Whole-document answers that genuinely combine evidence from across the document. |

### Implementation — 35%

| Criterion | Weight | What it measures |
|---|---|---|
| Requirements & API contract | 5 | Python/FastAPI, uv, Docker + Qdrant, the `/ingest` + `/query` contract, a real LLM interface. |
| Retrieval pipeline | 7 | Extraction, chunking, embeddings and search beyond the naive baseline. |
| **Conversational memory** | **10** | Maintaining conversation context across turns — the axis this hackathon is named for. History-aware retrieval that resolves a follow-up into a standalone query before retrieving. |
| Whole-document reasoning | 8 | Multi-query, agentic retrieval, a second index, or structure-aware table handling. |
| Code quality & structure | 3 | Clean, modular, readable, reasonably typed. |
| Architecture & design | 2 | Coherent design; sensible separation; room to extend. |

### Rigor — 20%

| Criterion | Weight | What it measures |
|---|---|---|
| Innovation & sophistication | 6 | A non-obvious technique that worked. |
| Measurement & self-evaluation | 5 | An ablation with numbers, a per-level breakdown, or a diagnosed failure. Honest negatives count. |
| Technical note | 5 | Claims backed by artefacts; technically accurate; low filler. |
| Reproducibility | 4 | Runs from the documented steps; deterministic enough to trust. |

### Integrity — 15%

| Criterion | Weight | What it measures |
|---|---|---|
| Level-appropriate approach | 5 | Respecting the complexity split. **Bonus** for exceeding a level; **penalty** for trivialising one. |
| Integrity — no gaming | 8 | No hardcoded/question-specific answers, no fabricated citations, no wrapper-only shortcut. |
| Documentation & usability | 2 | README, run steps, meaningful comments. |

## How the two halves combine

```
code_score  = weighted sum of the sixteen criteria           (0–100)
jury_score  = average of the jury's presentation marks        (0–100)
final_score = 0.5 × code_score + 0.5 × jury_score
```

## What earns and loses points

- **Build a real, general system.** Answers must come from your pipeline, not from branches keyed
  to the exact questions. Hardcoding, question-specific hacks and fabricated evidence quotes are
  penalised heavily under *Integrity*.
- **Respect the levels.** A Level-3 question answered by luck from a single chunk scores low on
  *Level-appropriate approach*; a genuinely strong whole-document method is rewarded there.
- **Ground every answer.** An evidence quote that does not appear in the document counts against
  both the answer criteria and *Integrity*.
- **Measure yourself.** An honest ablation — even a negative result — scores well; unsupported
  claims that "it works" do not.
- **Make it run.** A repo that others cannot build loses *Reproducibility* and puts the answer
  criteria in doubt.
