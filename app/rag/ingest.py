"""Load a PDF into the vector store.

    parse PDF (data/in) -> pages -> [chunk] -> embeddings -> Qdrant

By default there is no chunking (one vector per page) and embeddings come from a local
sentence-transformers model. Both are yours to improve (see chunking.py and embeddings.py).
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber
from pypdf import PdfReader
from qdrant_client import models

from ..config import get_settings
from ..models import IngestResponse
from ..vectorstore.qdrant_store import get_store
from .chunking import Chunk, chunk_pages
from .embeddings import get_embedder

_NAMESPACE = uuid.UUID("6f0d9b1e-3b7a-4c2e-9a1d-000000000000")

# Block types to skip entirely when using the Marker JSON renderer
_SKIP_BLOCK_TYPES = {"PageHeader", "PageFooter", "Picture", "Figure", "FigureGroup", "Diagram"}


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


def _section_breadcrumb(block) -> str:
    """Build a breadcrumb string from a block's section_hierarchy."""
    sh = getattr(block, "section_hierarchy", None) or {}
    if not sh:
        return ""
    # section_hierarchy maps depth -> block id; resolve titles via the rendered tree
    # We can't easily resolve ids here, so we use the block's own html to get the title
    # Instead we rely on the caller to track this — return empty and let the chunker handle it
    return ""


def _chunks_from_marker_json(path: Path, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """Use Marker's JSON renderer to build chunks with correct page numbers and section titles."""
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict

    embed_breadcrumbs = get_settings().embed_breadcrumbs

    converter = PdfConverter(
        artifact_dict=create_model_dict(),
        renderer="marker.renderers.json.JSONRenderer",
    )
    rendered = converter(str(path))

    # Build a map of block_id -> section header text for breadcrumb resolution
    header_text: dict[str, str] = {}
    for page in rendered.children or []:
        for block in page.children or []:
            if block.block_type == "SectionHeader":
                text = re.sub(r"<[^>]+>", "", block.html or "").strip()
                if text:
                    header_text[block.id] = text

    def _breadcrumb(block) -> str:
        sh = getattr(block, "section_hierarchy", None) or {}
        parts = [header_text[bid] for bid in sh.values() if bid in header_text]
        return " ".join(f"[{p}]" for p in parts)

    def _sliding(text: str) -> list[str]:
        if len(text) <= chunk_size:
            return [text]
        result = []
        start = 0
        while start < len(text):
            result.append(text[start : start + chunk_size])
            start += chunk_size - chunk_overlap
        return result

    chunks: list[Chunk] = []
    idx = 0
    for page in rendered.children or []:
        m = re.search(r"/page/(\d+)/", page.id)
        page_no = int(m.group(1)) + 1 if m else 0

        for block in page.children or []:
            if block.block_type in _SKIP_BLOCK_TYPES:
                continue
            raw = re.sub(r"<[^>]+>", "", block.html or "").strip()
            if not raw or len(raw) < 40:
                continue

            breadcrumb = _breadcrumb(block)
            title = breadcrumb
            full_text = f"{breadcrumb} {raw}" if (breadcrumb and embed_breadcrumbs) else raw

            for window in _sliding(full_text):
                chunks.append(Chunk(text=window, page=page_no, index=idx, title=title))
                idx += 1

    return chunks


def extract_pages(path: Path) -> list[str]:
    """Per-page text extraction, dispatched by PDF_READER in settings.

    TODO(level-1): pypdf is fine for clean digital PDFs and poor on complex layout
      (two columns, tables, ligatures, math). If your citations won't match the
      document, your extractor is usually why. Try pdfplumber, PyMuPDF, Docling,
      GROBID or Marker and keep whichever reads your document best.
    """
    reader = get_settings().pdf_reader.lower()
    if reader == "pymupdf":
        doc = fitz.open(str(path))
        return [(page.get_text() or "") for page in doc]
    if reader == "pypdf":
        return [(page.extract_text() or "") for page in PdfReader(str(path)).pages]
    if reader == "pdfplumber":
        with pdfplumber.open(str(path)) as pdf:
            return [(page.extract_text() or "") for page in pdf.pages]
    if reader == "marker":
        # Marker path uses JSON renderer for structured chunking — see _chunks_from_marker_json
        # This fallback returns raw markdown pages (unused when is_markdown=True)
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered

        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(str(path))
        text, _, _ = text_from_rendered(rendered)
        return [text]
    raise ValueError(
        f"unknown PDF_READER: {reader!r} (expected pypdf, pymupdf, pdfplumber or marker)"
    )


def ingest(filename: str | None = None, reset: bool = False) -> IngestResponse:
    settings = get_settings()
    embedder = get_embedder()
    store = get_store()

    path = _find_pdf(filename)

    if settings.pdf_reader.lower() == "marker":
        chunks = _chunks_from_marker_json(path, settings.chunk_size, settings.chunk_overlap)
        num_pages = max((c.page for c in chunks), default=0)
    else:
        pages = extract_pages(path)
        chunks = chunk_pages(pages, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
        num_pages = len(pages)

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
        pages=num_pages,
        chunks=len(chunks),
        collection=settings.qdrant_collection,
    )

