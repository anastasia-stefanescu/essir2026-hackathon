"""Find the chunks most relevant to a question."""

from __future__ import annotations

from dataclasses import dataclass

from ..llm.base import LLMError, Message
from ..llm.factory import get_client
from ..vectorstore.qdrant_store import get_store
from .embeddings import get_embedder


@dataclass
class Context:
    text: str
    page: int
    score: float
    title: str = ""


def rewrite_query(question: str, history: list[Message]) -> str:
    """Resolve a follow-up into a standalone search query.

    TODO(level-2): THIS IS THE KEY FUNCTION FOR CONVERSATIONAL RETRIEVAL and right
      now it is a no-op. "And the test split?" has no retrievable content on its own,
      so embedding it returns noise. Use the client's chat model to rewrite the
      question against `history` into something self-contained
      ("How large is the test split of <the dataset from the previous turn>?"),
      then retrieve with that. Leave genuinely standalone questions unchanged.
    """
    if not history:
        return question
    client = get_client()
    messages: list[Message] = [
        {
            "role": "system",
            "content": (
                "You rewrite follow-up questions into standalone search queries. "
                "Given the conversation history and a new question, output ONLY the "
                "rewritten query — a single sentence with no explanation. "
                "Resolve ambiguous references (e.g. 'that', 'it', 'this') using the "
                "most recent exchange in the conversation as the context with priority, as "
                "would happen in a natural conversation. "
                "If the question is already self-contained, output it unchanged."
            ),
        },
        *history,  # full history; most recent exchange has priority for disambiguation
        {
            "role": "user",
            "content": f"Rewrite this as a standalone query: {question}",
        },
    ]
    try:
        return client.chat(messages).strip()
    except LLMError:
        return question


def retrieve(question: str, top_k: int, history: list[Message] | None = None) -> tuple[list[Context], list[float], str]:
    embedder = get_embedder()
    store = get_store()

    query = rewrite_query(question, history or [])

    # TODO(level-3): one query + one search is not enough for whole-document
    #   questions ("summarise every chapter", "combine the table on p.40 with the
    #   reference on p.90"). Consider multi-query fan-out, iterative/agentic retrieval
    #   (retrieve -> reason -> retrieve again), or a second index (e.g. a graph or a
    #   per-section summary index) alongside this one.
    vector = embedder.embed([query], is_query=True)[0]
    hits = store.search(vector, top_k)

    contexts = [
        Context(
            text=str(h.payload.get("text", "")),
            page=int(h.payload.get("page", 0)),
            score=float(h.score),
            title=str(h.payload.get("title", "")),
        )
        for h in hits
    ]
    return contexts, vector, query
