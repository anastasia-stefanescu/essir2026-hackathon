"""Ollama provider — https://ollama.com

Talks to a local Ollama server over its native REST API. Pull models first:

    ollama pull llama3.1
    ollama pull nomic-embed-text
"""

from __future__ import annotations

import httpx

from .base import LLMError, Message


class OllamaClient:
    def __init__(self, base_url: str, chat_model: str, embedding_model: str, timeout: float):
        self.base_url = base_url.rstrip("/")
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.timeout = timeout

    def chat(self, messages: list[Message]) -> str:
        try:
            resp = httpx.post(
                f"{self.base_url}/api/chat",
                json={"model": self.chat_model, "messages": messages, "stream": False},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]
        except Exception as e:
            raise LLMError(f"ollama chat failed: {e}") from e

    def embed(self, texts: list[str]) -> list[list[float]]:
        # /api/embeddings takes ONE prompt per call, so we loop. Newer Ollama has a
        # batched /api/embed endpoint — TODO(level-1): switch to it to speed up ingest.
        try:
            resp = httpx.post(
                f"{self.base_url}/api/embed",
                json={"model": self.embedding_model, "input": texts},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()["embeddings"]
        except Exception as e:
            raise LLMError(f"ollama embed failed: {e}") from e
