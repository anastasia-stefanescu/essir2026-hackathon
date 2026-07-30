"""Turn PDF pages into the units you index.

**Chunking is OFF by default.** Out of the box each page becomes exactly one vector — no
splitting, no overlap. That is the simplest thing that runs, and it is deliberately weak:
a whole page is often too long for the embedding model (it gets truncated) and too coarse
to retrieve precisely.

Implementing real chunking is one of the first things that will improve your Level-1 scores.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    page: int  # 1-indexed
    index: int  # position within the document
    title: str = ""  # breadcrumb path, e.g. "2. Methods > 2.2.1. Annotation"


# Matches any markdown heading line: #, ##, ###, etc.
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
# Extracts a section number prefix like "3.2.1" from a heading title
_SECTION_NUM_RE = re.compile(r"^(\d+(?:\.\d+)*)\.")
# Matches a footnote line moved to end of page by _reflow_marker_page: <sup>N</sup>...
_FOOTNOTE_LINE_RE = re.compile(r"^(<sup>\d+<\/sup>.+)$", re.MULTILINE)
# Matches an inline footnote reference inside paragraph body: <sup>N</sup>
_FOOTNOTE_REF_RE = re.compile(r"<sup>(\d+)<\/sup>")
# Matches a paragraph that is only an image reference
_IMAGE_ONLY_RE = re.compile(r"^!\[.*?\]\(.*?\)\.?$", re.DOTALL)
# Matches an inline label at the start of a paragraph, e.g. "Objective:", "Methods:"
_INLINE_LABEL_RE = re.compile(r"^([A-Z][A-Za-z /\-]{0,40}):")
_MIN_CONTENT_LEN = 40  # discard chunks shorter than this


def _sliding_window(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into overlapping character windows."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks


def _chunk_markdown(pages: list[str], chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """Structure-aware chunking for Marker markdown output.

    Each chunk gets a breadcrumb prefix showing its position in the document
    (e.g. "2. Methods > 2.2. Detection > 2.2.1. Annotation") and any footnotes
    referenced inline are appended at the end of the chunk.
    """
    # Build a page-lookup so we can assign page numbers to paragraphs.
    # Each page is a string; we tag paragraphs with the page they came from.
    tagged: list[tuple[int, str]] = []  # (page_no, paragraph_text)
    for page_no, page_text in enumerate(pages, start=1):
        # Separate footnote lines from body (already reflowed by _reflow_marker_page)
        footnotes = dict(
            (m.group(1).lstrip("<sup>").rstrip("</sup>"), m.group(0))  # num -> full line
            for m in re.finditer(r"^<sup>(\d+)<\/sup>.+$", page_text, re.MULTILINE)
        )
        body = _FOOTNOTE_LINE_RE.sub("", page_text)
        for para in body.split("\n\n"):
            para = para.strip()
            if para and not _IMAGE_ONLY_RE.match(para):
                tagged.append((page_no, para, footnotes))  # type: ignore[arg-type]

    # Walk tagged paragraphs, maintaining a heading breadcrumb stack.
    breadcrumb_stack: list[tuple[int, str]] = []  # (level, title)
    chunks: list[Chunk] = []
    idx = 0

    for page_no, para, footnotes in tagged:  # type: ignore[misc]
        heading_match = _HEADING_RE.match(para)
        if heading_match:
            title = heading_match.group(2).strip()
            num_match = _SECTION_NUM_RE.match(title)
            if num_match:
                level = num_match.group(1).count(".") + 1
            else:
                level = len(heading_match.group(1))
            breadcrumb_stack = [(l, t) for l, t in breadcrumb_stack if l < level]
            breadcrumb_stack.append((level, title))
            continue

        breadcrumb = " ".join(f"[{t}]" for _, t in breadcrumb_stack)
        ref_nums = _FOOTNOTE_REF_RE.findall(para)
        matched_footnotes = [footnotes[n] for n in ref_nums if n in footnotes]
        body = para
        if matched_footnotes:
            body = para + "\n\n" + "\n".join(matched_footnotes)

        # Drop paragraphs whose content (excluding images) is too short to be useful
        content_only = re.sub(r"!\[.*?\]\(.*?\)", "", body).strip()
        if len(content_only) < _MIN_CONTENT_LEN:
            continue

        inline_label = _INLINE_LABEL_RE.match(para)
        title = f"{breadcrumb} [{inline_label.group(1)}]" if inline_label else breadcrumb
        full_text = f"{breadcrumb} {body}" if breadcrumb else body
        for window in _sliding_window(full_text, chunk_size, chunk_overlap):
            chunks.append(Chunk(text=window, page=page_no, index=idx, title=title))
            idx += 1

    return chunks


def chunk_pages(
    pages: list[str],
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    is_markdown: bool = False,
) -> list[Chunk]:
    """Split pages into retrievable chunks.

    TODO(level-1): THIS IS WHERE CHUNKING GOES, and right now there is none. Split each
      page into retrievable units — by tokens, by sentences/paragraphs, or structure-aware
      (headings, tables). Keep the correct `page` on each piece so citations still line up.
      Good chunking is usually the single biggest win for retrieval quality.
    TODO(level-3): a flat chunk loses where it sits in the document. Section titles, or a
      small/large ("parent") hierarchy, help a lot with whole-document questions.

    The settings `chunk_size` / `chunk_overlap` exist for when you implement this — they are
    unused by the baseline.

    When is_markdown=True (Marker output), uses structure-aware splitting on
    headings and paragraphs with breadcrumb prefixes. Otherwise falls back to
    sliding-window character splitting with overlap.
    """
    if is_markdown:
        return _chunk_markdown(pages, chunk_size, chunk_overlap)

    chunks: list[Chunk] = []
    idx = 0
    for page_no, text in enumerate(pages, start=1):
        text = text.strip()
        if not text:
            continue
        for window in _sliding_window(text, chunk_size, chunk_overlap):
            chunks.append(Chunk(text=window, page=page_no, index=idx))
            idx += 1
    return chunks
