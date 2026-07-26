"""Turn PDF pages into the units you index.

**Chunking is OFF by default.** Out of the box each page becomes exactly one vector — no
splitting, no overlap. That is the simplest thing that runs, and it is deliberately weak:
a whole page is often too long for the embedding model (it gets truncated) and too coarse
to retrieve precisely.

Implementing real chunking is one of the first things that will improve your Level-1 scores.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    page: int      # 1-indexed
    index: int     # position within the document


def chunk_pages(pages: list[str]) -> list[Chunk]:
    """Default: one chunk per page (no chunking).

    TODO(level-1): THIS IS WHERE CHUNKING GOES, and right now there is none. Split each
      page into retrievable units — by tokens, by sentences/paragraphs, or structure-aware
      (headings, tables). Keep the correct `page` on each piece so citations still line up.
      Good chunking is usually the single biggest win for retrieval quality.
    TODO(level-3): a flat chunk loses where it sits in the document. Section titles, or a
      small/large ("parent") hierarchy, help a lot with whole-document questions.

    The settings `chunk_size` / `chunk_overlap` exist for when you implement this — they are
    unused by the baseline.
    """
    chunks: list[Chunk] = []
    idx = 0
    for page_no, text in enumerate(pages, start=1):
        text = text.strip()
        if not text:
            continue
        chunks.append(Chunk(text=text, page=page_no, index=idx))
        idx += 1
    return chunks
