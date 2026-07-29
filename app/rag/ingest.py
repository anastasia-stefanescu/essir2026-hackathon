"""Load a PDF into the vector store.

    parse PDF (data/in) -> pages -> [chunk] -> embeddings -> Qdrant

By default there is no chunking (one vector per page) and embeddings come from a local
sentence-transformers model. Both are yours to improve (see chunking.py and embeddings.py).
"""

from __future__ import annotations

import uuid
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber
from pypdf import PdfReader
from qdrant_client import models

from ..config import get_settings
from ..models import IngestResponse
from ..vectorstore.qdrant_store import get_store
from .chunking import chunk_pages
from .embeddings import get_embedder

import re

_NAMESPACE = uuid.UUID("6f0d9b1e-3b7a-4c2e-9a1d-000000000000")


def _reflow_marker_page(text: str) -> str:
    """Move inline footnote paragraphs to the end of the page."""
    footnote_pattern = re.compile(r"^(<sup>\d+<\/sup>.+)$", re.MULTILINE)
    footnotes = footnote_pattern.findall(text)
    if not footnotes:
        return text
    body = footnote_pattern.sub("", text).strip()
    return body + "\n\n" + "\n".join(footnotes)


def _find_pdf(filename: str | None) -> Path:
    in_dir = Path(get_settings().in_dir)
    if filename:
        path = in_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"no such PDF: {path}")
        return path
    pdfs = sorted(in_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"no *.pdf found in {in_dir}/ — put your document there first")
    return pdfs[0]


def extract_pages(path: Path) -> list[str]:
    """Per-page text extraction, dispatched by PDF_READER in settings.

    TODO(level-1): pypdf is fine for clean digital PDFs and poor on complex layout
      (two columns, tables, ligatures, math). If your citations won't match the
      document, your extractor is usually why. Try pdfplumber, PyMuPDF, Docling,
      GROBID or Marker and keep whichever reads your document best.
    """
    reader = get_settings().pdf_reader.lower()
    print("Current reader", reader)
    if reader == "pymupdf":
        doc = fitz.open(str(path))
        return [(page.get_text() or "") for page in doc]
    if reader == "pypdf":
        return [(page.extract_text() or "") for page in PdfReader(str(path)).pages]
    if reader == "pdfplumber":
        with pdfplumber.open(str(path)) as pdf:
            return [(page.extract_text() or "") for page in pdf.pages]
    if reader == "marker":
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered

        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(str(path))
        text, _, _ = text_from_rendered(rendered)
        # marker returns one markdown string; split on page-break markers
        raw_pages = text.split("\f")
        pages = [p.strip() for p in raw_pages] if len(raw_pages) > 1 else [text]
        return [_reflow_marker_page(p) for p in pages]
    raise ValueError(
        f"unknown PDF_READER: {reader!r} (expected pypdf, pymupdf, pdfplumber or marker)"
    )


def ingest(filename: str | None = None, reset: bool = False) -> IngestResponse:
    settings = get_settings()
    embedder = get_embedder()
    store = get_store()

    path = _find_pdf(filename)
    pages = extract_pages(path)
    chunks = chunk_pages(
        pages,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        is_markdown=(settings.pdf_reader.lower() == "marker"),
    )
    print(chunks)
    if not chunks:
        raise ValueError(f"{path.name} produced no text — is it a scanned/image PDF?")

    # Embed in batches. is_query=False marks these as documents ("passage:" for e5).
    vectors: list[list[float]] = []
    batch = 32
    for i in range(0, len(chunks), batch):
        texts = [c.text for c in chunks[i : i + batch]]
        vectors.extend(embedder.embed(texts, is_query=False))

    store.ensure_collection(dim=len(vectors[0]), reset=reset)

    points = [
        models.PointStruct(
            id=str(uuid.uuid5(_NAMESPACE, f"{path.name}:{c.index}")),
            vector=vec,
            payload={"text": c.text, "page": c.page, "source": path.name, "title": c.title},
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
