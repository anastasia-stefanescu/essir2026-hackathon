"""Inspect the vector store."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..vectorstore.qdrant_store import get_store

router = APIRouter(tags=["vectorstore"])


@router.get("/collections")
def list_collections() -> dict:
    """List Qdrant collections and the point count in the active one."""
    store = get_store()
    try:
        return {
            "collections": store.list_collections(),
            "active": store.collection,
            "points": store.count(),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"qdrant unreachable: {e}") from e
