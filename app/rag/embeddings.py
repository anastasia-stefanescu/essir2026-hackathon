"""Embeddings — turning text into vectors.

**This is a starting point you are meant to improve.** Out of the box we embed with a
local sentence-transformers model (`intfloat/multilingual-e5-large`) so the app runs with
no embedding API and no configuration. It is a solid multilingual baseline — but the choice
of model, how you build the text you embed, and how you chunk it are all yours to tune.

`get_embedder()` returns an object with `embed(texts, is_query=False)`. Two backends:
  - "sentence-transformers" (default): local, downloads the model on first use.
  - "provider": reuse the chat provider's embed() (Ollama / LM Studio / litellm).
"""

from __future__ import annotations

from functools import lru_cache

from ..config import get_settings


class SentenceTransformerEmbedder:
    """Local embeddings via sentence-transformers.

    The e5 family expects each text to be prefixed with "query: " or "passage: "; we do
    that automatically. If you switch to a model that does NOT use these prefixes (e.g.
    BGE, GTE, nomic), drop them — see `_prefix`.
    """

    def __init__(self, model_name: str):
        # Imported lazily so the app imports even before the (large) dep is installed.
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        self._is_e5 = "e5" in model_name.lower()

    def _prefix(self, text: str, is_query: bool) -> str:
        if not self._is_e5:
            return text
        return f"{'query' if is_query else 'passage'}: {text}"

    def embed(self, texts: list[str], is_query: bool = False) -> list[list[float]]:
        prepared = [self._prefix(t, is_query) for t in texts]
        vecs = self._model.encode(prepared, normalize_embeddings=True)
        return [v.tolist() for v in vecs]


class ProviderEmbedder:
    """Embeddings from the chat provider (set embedding_backend=provider)."""

    def __init__(self):
        from ..llm.factory import get_client

        self._client = get_client()

    def embed(self, texts: list[str], is_query: bool = False) -> list[list[float]]:
        # Most embedding APIs do not distinguish query vs passage; is_query is ignored.
        return self._client.embed(texts)


@lru_cache
def get_embedder():
    s = get_settings()
    backend = s.embedding_backend.lower()
    if backend in ("sentence-transformers", "sentence_transformers", "st"):
        return SentenceTransformerEmbedder(s.embedding_model)
    if backend == "provider":
        return ProviderEmbedder()
    raise ValueError(
        f"unknown embedding_backend: {s.embedding_backend!r} "
        "(expected 'sentence-transformers' or 'provider')"
    )
