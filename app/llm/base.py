"""The contract every provider implements.

A client is anything with `chat()` and `embed()`. Keeping this narrow means the
rest of the app (`app/rag/`) never cares which backend is running.
"""

from __future__ import annotations

from typing import Protocol, TypedDict


class Message(TypedDict):
    role: str  # "system" | "user" | "assistant"
    content: str


class ChatModel(Protocol):
    def chat(self, messages: list[Message]) -> str:
        """Return the assistant's reply to a list of chat messages."""
        ...


class EmbeddingModel(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text, in order."""
        ...


class LLMError(RuntimeError):
    """Raised when a provider call fails. Callers decide whether to degrade or surface it."""
