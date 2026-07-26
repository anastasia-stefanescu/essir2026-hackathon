"""Turn PDF pages into chunks.

The baseline is deliberately crude: fixed-size character windows within each page.
It keeps page attribution exact (a chunk never straddles two pages) but it will
happily cut a sentence — or a table row — in half.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import get_settings


@dataclass
class Chunk:
    text: str
    page: int      # 1-indexed
    index: int     # position within the document


def chunk_pages(pages: list[str]) -> list[Chunk]:
    """Split each page into overlapping character windows.

    TODO(level-1): character windows are the weakest reasonable choice. Consider
      token-based sizing, sentence/paragraph boundaries, or structure-aware
      (headings, tables) chunking. Bad chunks are the most common reason a correct
      answer is un-retrievable.
    TODO(level-3): a chunk loses the page's place in the document. Keeping section
      titles, or a small/large ("parent") chunk hierarchy, helps whole-document
      questions a lot.
    """
    s = get_settings()
    size, overlap = s.chunk_size, s.chunk_overlap
    step = max(1, size - overlap)

    chunks: list[Chunk] = []
    idx = 0
    for page_no, text in enumerate(pages, start=1):
        text = text.strip()
        if not text:
            continue
        start = 0
        while start < len(text):
            window = text[start : start + size].strip()
            if window:
                chunks.append(Chunk(text=window, page=page_no, index=idx))
                idx += 1
            start += step
    return chunks
