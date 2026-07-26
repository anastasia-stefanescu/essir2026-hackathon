"""FastAPI application.

    uv run uvicorn app.main:app --reload        # local
    docker compose up --build                   # containers + Qdrant

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from . import __version__
from .routes import collections, health, ingest, query

DESCRIPTION = """
A retrieval-augmented-generation backend over one PDF, for **The Fourth Turn**
(ESSIR 2026 hackathon).

**Typical flow**

1. `POST /ingest` — index the PDF sitting in `data/`.
2. `POST /query` — ask a question. The response is what you submit.

The scaffold answers Level-1 questions out of the box. Level 2 (conversational
memory) and Level 3 (whole-document reasoning) are yours to build — follow the
`TODO(level-N)` markers in `app/rag/` and `app/llm/`.
"""


def create_app() -> FastAPI:
    app = FastAPI(
        title="The Fourth Turn",
        version=__version__,
        description=DESCRIPTION,
    )

    app.include_router(health.router)
    app.include_router(collections.router)
    app.include_router(ingest.router)
    app.include_router(query.router)

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()
