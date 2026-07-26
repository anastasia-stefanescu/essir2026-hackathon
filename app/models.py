"""Request and response schemas.

The `QueryResponse` below IS the format we grade. When you answer one of the nine
challenge questions, the JSON your `POST /query` endpoint returns is exactly what
you save into `results/level-N/qM.json` — copy it verbatim. See `results/README.md`
and `templates/answer.example.json`.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Source(BaseModel):
    """One piece of evidence supporting an answer.

    `quote` must be text that actually appears in the PDF on `page` — it is how we
    (and you) check the answer is grounded in the document rather than invented.
    """

    page: int = Field(..., description="1-indexed PDF page the quote is on")
    quote: str = Field(..., description="verbatim span from the PDF that supports the answer")
    score: float | None = Field(None, description="retrieval score, if you have one")


class Diagnostics(BaseModel):
    """Self-reported, not graded for correctness — but you should be able to explain it."""

    provider: str
    chat_model: str
    embedding_model: str
    retrieved_chunks: int
    tokens: int | None = None
    latency_ms: int | None = None


class QueryRequest(BaseModel):
    question: str = Field(..., description="the question to answer")
    question_id: str | None = Field(None, description="e.g. 'q4' — echoed back into the response")
    level: int | None = Field(None, description="1, 2 or 3 — echoed back into the response")
    conversation_id: str | None = Field(
        None,
        description=(
            "Group turns into a conversation. Level-2 questions are follow-ups: send "
            "them with the SAME conversation_id as the question they depend on, so your "
            "system can use the history. Omit it and each query is standalone."
        ),
    )
    top_k: int | None = Field(None, description="override the configured retrieval depth")


class QueryResponse(BaseModel):
    """The graded object. Save this, unchanged, as results/level-N/qM.json."""

    question_id: str | None = None
    level: int | None = None
    question: str
    answer: str
    conversation_id: str | None = None
    sources: list[Source] = Field(default_factory=list)
    diagnostics: Diagnostics | None = None


class IngestRequest(BaseModel):
    filename: str | None = Field(
        None, description="a PDF under data/; defaults to the first *.pdf found"
    )
    reset: bool = Field(False, description="drop and recreate the collection before ingesting")


class IngestResponse(BaseModel):
    document: str
    pages: int
    chunks: int
    collection: str
