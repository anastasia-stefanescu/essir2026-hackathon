"""Load the corpus PDF into the vector store."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import IngestRequest, IngestResponse
from ..rag.ingest import ingest

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
def ingest_document(req: IngestRequest) -> IngestResponse:
    """Parse, chunk, embed and index a PDF from `data/`.

    Run this once (per document, or after you change chunking/embeddings) before
    querying. Pass `reset: true` to rebuild the collection from scratch.
    """
    try:
        return ingest(filename=req.filename, reset=req.reset)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ingest failed: {e}") from e
