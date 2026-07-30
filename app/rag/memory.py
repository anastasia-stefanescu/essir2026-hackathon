"""Conversation memory — where Level 2 lives.

A Level-2 question is a follow-up: *"and how large is its test split?"* only makes
sense given the earlier turn it refers to. To answer it you need the history of the
conversation it belongs to.

When REDIS_URL is set (always the case in Docker), history is stored in Redis and
survives restarts and scales across workers. When it is not set (local uv run without
Redis), falls back to an in-process dict.
"""

from __future__ import annotations

import json

from ..config import get_settings
from ..llm.base import Message

# Fallback in-process store (local dev without Redis)
_STORE: dict[str, list[Message]] = {}

_REDIS_KEY_PREFIX = "memory:"
_REDIS_TTL = 60 * 60 * 24  # 24 hours


def _redis():
    url = get_settings().redis_url
    if not url:
        return None
    import redis
    return redis.from_url(url, decode_responses=True)


def get_history(conversation_id: str | None) -> list[Message]:
    if not conversation_id:
        return []
    r = _redis()
    if r is not None:
        raw = r.get(f"{_REDIS_KEY_PREFIX}{conversation_id}")
        return json.loads(raw) if raw else []
    return list(_STORE.get(conversation_id, []))


def append(conversation_id: str | None, user: str, assistant: str) -> None:
    if not conversation_id:
        return
    r = _redis()
    if r is not None:
        key = f"{_REDIS_KEY_PREFIX}{conversation_id}"
        raw = r.get(key)
        history: list[Message] = json.loads(raw) if raw else []
        history.append({"role": "user", "content": user})
        history.append({"role": "assistant", "content": assistant})
        r.set(key, json.dumps(history), ex=_REDIS_TTL)
    else:
        history = _STORE.setdefault(conversation_id, [])
        history.append({"role": "user", "content": user})
        history.append({"role": "assistant", "content": assistant})


def reset(conversation_id: str) -> None:
    r = _redis()
    if r is not None:
        r.delete(f"{_REDIS_KEY_PREFIX}{conversation_id}")
    else:
        _STORE.pop(conversation_id, None)


# TODO(level-2): history alone is not enough. The retrieval step still embeds the
#   raw follow-up ("and the test split?"), which has no searchable content. The high-
#   leverage fix is to REWRITE the question into a standalone query using this history
#   BEFORE retrieving — see rag/retrieve.py::rewrite_query.
# TODO(level-2): a persistent, shared store (Redis, Postgres, ...) if you run more
#   than one worker or want memory to survive a restart.
