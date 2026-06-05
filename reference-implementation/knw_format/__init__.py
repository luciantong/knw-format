"""
knw_format — Reference implementation of the .knw open document format.

Usage:
    from knw_format import KnwDocument, OntologyNode

    doc = KnwDocument.load("my-file.ai")
    print(doc.content)
    print(doc.ontology.nodes)
"""

from .document import KnwDocument
from .ontology import OntologyNode, OntologyGraph
from .memory import MemoryLayer, DeltaItem
from .embeddings import (
    LocalEmbeddingBackend,
    OpenAIEmbeddingBackend,
    StubEmbeddingBackend,
    get_default_backend,
)

__version__ = "0.1.0"
__spec_version__ = "knw/1.0"
__all__ = [
    "KnwDocument",
    "OntologyNode",
    "OntologyGraph",
    "MemoryLayer",
    "DeltaItem",
    "LocalEmbeddingBackend",
    "OpenAIEmbeddingBackend",
    "StubEmbeddingBackend",
    "get_default_backend",
]
