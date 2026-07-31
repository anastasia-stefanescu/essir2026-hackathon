"""Sparse vector encoders for hybrid search.

Three backends with the same interface:
  encode(texts) -> list of {token_id: weight} dicts

Select via SPARSE_ENCODER in .env (or settings.sparse_encoder):
  "fastembed"  -> SPLADE via fastembed  (lightweight, recommended)
  "splade"     -> SPLADE via transformers (higher quality, ~500 MB model download)
  "tfidf"      -> TF-IDF via sklearn    (no download, lowest quality)

Only used when SEARCH_MODE is "sparse" or "hybrid".
"""

from __future__ import annotations

from functools import lru_cache


class FastEmbedSparseEncoder:
    """SPLADE-style sparse encoder backed by fastembed."""

    MODEL = "prithivida/Splade_PP_en_v1"

    def __init__(self) -> None:
        from fastembed.sparse import SparseTextEmbedding
        self._model = SparseTextEmbedding(model_name=self.MODEL)

    def encode(self, texts: list[str]) -> list[dict[int, float]]:
        results = list(self._model.embed(texts))
        out = []
        for r in results:
            out.append({int(i): float(v) for i, v in zip(r.indices, r.values)})
        return out


class SpladeSparseEncoder:
    """SPLADE encoder using transformers directly."""

    MODEL = "naver/splade-cocondenser-ensembledistil"

    def __init__(self) -> None:
        import torch
        from transformers import AutoModelForMaskedLM, AutoTokenizer
        self._tokenizer = AutoTokenizer.from_pretrained(self.MODEL)
        self._model = AutoModelForMaskedLM.from_pretrained(self.MODEL)
        self._model.eval()
        self._torch = torch

    def encode(self, texts: list[str]) -> list[dict[int, float]]:
        import torch
        out = []
        for text in texts:
            tokens = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                logits = self._model(**tokens).logits
            # SPLADE aggregation: max(0, log(1 + relu(logits))) pooled over tokens
            vec = torch.log1p(torch.relu(logits)).max(dim=1).values.squeeze(0)
            indices = vec.nonzero(as_tuple=True)[0].tolist()
            values = vec[indices].tolist()
            out.append({int(i): float(v) for i, v in zip(indices, values)})
        return out


class TfidfSparseEncoder:
    """TF-IDF sparse encoder using sklearn. Fits vocabulary at first encode call."""

    def __init__(self) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._vectorizer = TfidfVectorizer()
        self._fitted = False

    def encode(self, texts: list[str]) -> list[dict[int, float]]:
        if not self._fitted:
            self._vectorizer.fit(texts)
            self._fitted = True
        matrix = self._vectorizer.transform(texts)
        out = []
        for i in range(matrix.shape[0]):
            row = matrix.getrow(i)
            out.append({int(idx): float(val) for idx, val in zip(row.indices, row.data)})
        return out


@lru_cache(maxsize=1)
def get_sparse_encoder():
    from ..config import get_settings
    backend = get_settings().sparse_encoder.lower()
    if backend == "fastembed":
        return FastEmbedSparseEncoder()
    if backend == "splade":
        return SpladeSparseEncoder()
    if backend == "tfidf":
        return TfidfSparseEncoder()
    raise ValueError(f"unknown sparse_encoder: {backend!r} (expected fastembed, splade, tfidf)")
