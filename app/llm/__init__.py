"""LLM and embedding providers.

Three interfaces are scaffolded — Ollama, LM Studio, and litellm (hosted APIs).
Each exposes the same two methods, `chat()` and `embed()`, defined in `base.py`.
`factory.get_client()` picks one from `LLM_PROVIDER`.

Need a provider that isn't here (vLLM, TGI, a bespoke gateway)? Implement the
`ChatModel` / `EmbeddingModel` protocols in a new module and wire it into the
factory. That is the intended extension point.
"""
