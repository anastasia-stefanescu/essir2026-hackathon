"""The main endpoint: answer a question about the document.

The response body is the object you submit. After you run each of the nine
challenge questions through here, copy the JSON response into the matching
`results/level-N/qM.json`. See docs/06_submission.md.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import QueryRequest, QueryResponse
from ..rag.pipeline import answer

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    """Answer a question, grounded in the ingested document.

    - Level 1: ask a standalone question.
    - Level 2: send follow-ups with the SAME `conversation_id` as the question they
      build on, so your system has the history.
    - Level 3: whole-document questions — the baseline will struggle; this is where
      you build (see the TODOs in app/rag/).
    """
    if not req.question.strip():
        raise HTTPException(status_code=422, detail="question must not be empty")
    try:
        return answer(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"query failed: {e}") from e
