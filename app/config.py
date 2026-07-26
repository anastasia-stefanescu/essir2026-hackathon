"""Application settings.

Values come from environment variables, or from a `.env` file (see `.env.example`).
Read once and cached — call `get_settings()` anywhere you need configuration.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- LLM provider -------------------------------------------------------
    # One of: "ollama", "lmstudio", "litellm". See app/llm/factory.py.
    llm_provider: str = "ollama"
    chat_model: str = "llama3.1"
    embedding_model: str = "nomic-embed-text"

    # --- Provider endpoints -------------------------------------------------
    ollama_base_url: str = "http://localhost:11434"
    lmstudio_base_url: str = "http://localhost:1234"
    litellm_api_base: str | None = None
    litellm_api_key: str | None = None

    # --- Qdrant -------------------------------------------------------------
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "fourth_turn"

    # --- Retrieval knobs ----------------------------------------------------
    # These are the obvious dials to turn. They are almost certainly not optimal.
    chunk_size: int = 800          # characters per chunk (TODO(level-1): try token-based)
    chunk_overlap: int = 150       # characters shared between neighbours
    top_k: int = 5                 # chunks retrieved per query

    # --- Misc ---------------------------------------------------------------
    data_dir: str = "data"
    request_timeout: float = 120.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
