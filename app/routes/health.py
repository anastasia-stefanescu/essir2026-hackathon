"""Liveness and readiness."""

from __future__ import annotations

from fastapi import APIRouter

from ..config import get_settings
from ..vectorstore.qdrant_store import get_store

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Is the app up? (Does not touch Qdrant or the LLM.)"""
    return {"status": "ok"}


@router.get("/health/ready")
def ready() -> dict:
    """Is the app ready to serve — i.e. can it reach Qdrant?"""
    s = get_settings()
    try:
        collections = get_store().list_collections()
        return {
            "status": "ready",
            "qdrant": "up",
            "collections": collections,
            "provider": s.llm_provider,
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "degraded", "qdrant": f"unreachable: {e}"}
