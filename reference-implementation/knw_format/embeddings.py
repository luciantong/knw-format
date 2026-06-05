"""
knw_format.embeddings
Pluggable embedding generation for .knw files.

The spec does not mandate a specific embedding model.
This module provides adapters for common backends.
Default: local sentence-transformers (no API key required).
"""

from typing import Protocol


class EmbeddingBackend(Protocol):
    """Interface that any embedding backend must implement."""

    def embed(self, text: str) -> list[float]:
        """Return a float vector for the given text."""
        ...


class LocalEmbeddingBackend:
    """
    Local embedding using sentence-transformers.
    No API key. Runs on CPU. Recommended for privacy-first use.

    Install: pip install sentence-transformers
    Default model: nomic-ai/nomic-embed-text-v1 (768 dimensions)
    """

    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v1"):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for local embeddings. "
                    "Install with: pip install sentence-transformers"
                )

    def embed(self, text: str) -> list[float]:
        self._load()
        return self._model.encode(text).tolist()


class OpenAIEmbeddingBackend:
    """
    OpenAI embedding via API.
    Requires OPENAI_API_KEY environment variable.
    Default model: text-embedding-3-small (1536 dimensions)
    """

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model

    def embed(self, text: str) -> list[float]:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )
        import os
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.embeddings.create(input=text, model=self.model)
        return response.data[0].embedding


class StubEmbeddingBackend:
    """
    Stub backend for testing — returns a zero vector.
    Do not use in production.
    """

    def __init__(self, dimensions: int = 8):
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        return [0.0] * self.dimensions


def get_default_backend() -> EmbeddingBackend:
    """
    Return the best available embedding backend.
    Tries local first (privacy-preserving), falls back to stub.
    """
    try:
        import sentence_transformers
        return LocalEmbeddingBackend()
    except ImportError:
        pass

    try:
        import openai
        import os
        if os.environ.get("OPENAI_API_KEY"):
            return OpenAIEmbeddingBackend()
    except ImportError:
        pass

    return StubEmbeddingBackend()
