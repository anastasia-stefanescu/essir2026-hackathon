"""Load a PDF into the vector store.

    parse PDF -> pages -> chunks -> embeddings -> Qdrant
"""

from __future__ import annotations

import uuid
from pathlib import Path

from pypdf import PdfReader
from qdrant_client import models

from ..config import get_settings
from ..llm.factory import get_client
from ..models import IngestResponse
from ..vectorstore.qdrant_store import get_store
from .chunking import chunk_pages

# A fixed namespace so re-ingesting the same document overwrites its points
# (idempotent ids) instead of duplicating them.
_NAMESPACE = uuid.UUID("6f0d9b1e-3b7a-4c2e-9a1d-000000000000")


def _find_pdf(filename: str | None) -> Path:
    data_dir = Path(get_settings().data_dir)
    if filename:
        path = data_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"no such PDF: {path}")
        return path
    pdfs = sorted(data_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"no *.pdf found in {data_dir}/ — put the corpus there first")
    return pdfs[0]


def extract_pages(path: Path) -> list[str]:
    """Per-page text via pypdf.

    TODO(level-1): pypdf is fine for clean digital PDFs and poor on complex layout
      (two columns, tables, ligatures, math). If your citations won't match the
      document, your extractor is usually why. Try pdfplumber, PyMuPDF, Docling,
      GROBID or Marker and keep whichever reads your paper best.
    """
    reader = PdfReader(str(path))
    return [(page.extract_text() or "") for page in reader.pages]


def ingest(filename: str | None = None, reset: bool = False) -> IngestResponse:
    settings = get_settings()
    client = get_client()
    store = get_store()

    path = _find_pdf(filename)
    pages = extract_pages(path)
    chunks = chunk_pages(pages)
    if not chunks:
        raise ValueError(f"{path.name} produced no text — is it a scanned/image PDF?")

    # Embed in batches so a big document doesn't become one giant request.
    vectors: list[list[float]] = []
    batch = 32
    for i in range(0, len(chunks), batch):
        texts = [c.text for c in chunks[i : i + batch]]
        vectors.extend(client.embed(texts))

    store.ensure_collection(dim=len(vectors[0]), reset=reset)

    points = [
        models.PointStruct(
            id=str(uuid.uuid5(_NAMESPACE, f"{path.name}:{c.index}")),
            vector=vec,
            payload={"text": c.text, "page": c.page, "source": path.name},
        )
        for c, vec in zip(chunks, vectors)
    ]
    store.upsert(points)

    return IngestResponse(
        document=path.name,
        pages=len(pages),
        chunks=len(chunks),
        collection=settings.qdrant_collection,
    )
