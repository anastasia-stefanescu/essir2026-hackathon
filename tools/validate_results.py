#!/usr/bin/env python3
"""Validate your results/ before you push.

    python tools/validate_results.py

Checks all nine answer files: they parse, sit in the right level folder, carry the
right question_id, and are actually filled in. Standard library only.

Exit 0 = ready to push. Exit 1 = problems printed below.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# (level, question_ids) - the expected layout under results/.
LAYOUT = {
    1: ["q1", "q2", "q3"],
    2: ["q4", "q5", "q6"],
    3: ["q7", "q8", "q9"],
}

errors: list[str] = []
warnings: list[str] = []


def check_file(path: Path, level: int, qid: str) -> None:
    if not path.is_file():
        errors.append(f"{path}: missing - every question must have a file")
        return

    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        errors.append(f"{path}: invalid JSON ({e}) - scores 0 for this question")
        return

    if not isinstance(data, dict):
        errors.append(f"{path}: top level must be a JSON object")
        return

    if str(data.get("question_id") or "") != qid:
        errors.append(f"{path}: question_id is {data.get('question_id')!r}, expected {qid!r}")

    if data.get("level") != level:
        errors.append(f"{path}: level is {data.get('level')!r}, expected {level}")

    if not str(data.get("question") or "").strip():
        warnings.append(f"{path}: 'question' is empty - paste the released question text")

    if not str(data.get("answer") or "").strip():
        errors.append(f"{path}: 'answer' is empty - this question scores 0")

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        warnings.append(
            f"{path}: no 'sources' - an answer without a grounding quote cannot be "
            f"confirmed and is capped (see docs/05_evaluation.md)"
        )
    else:
        for i, src in enumerate(sources):
            if not isinstance(src, dict):
                errors.append(f"{path}: sources[{i}] must be an object")
                continue
            if not str(src.get("quote") or "").strip():
                warnings.append(f"{path}: sources[{i}] has an empty quote")
            page = src.get("page")
            if not isinstance(page, int) or isinstance(page, bool) or page < 1:
                warnings.append(f"{path}: sources[{i}] page should be a positive integer (got {page!r})")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    results = root / "results"
    if not results.is_dir():
        print(f"[error] {results} not found - run from the repo root", file=sys.stderr)
        return 1

    total = 0
    for level, qids in LAYOUT.items():
        for qid in qids:
            total += 1
            check_file(results / f"level-{level}" / f"{qid}.json", level, qid)

    print(f"Checked {total} answer file(s) under {results}")
    for w in warnings:
        print(f"  [warn]  {w}")
    for e in errors:
        print(f"  [ERROR] {e}")

    if errors:
        print(f"\n[FAIL] {len(errors)} error(s). Fix these before you push.")
        return 1
    print("\n[OK] all nine answers present and filled in"
          + (f" - {len(warnings)} warning(s) worth a look" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
