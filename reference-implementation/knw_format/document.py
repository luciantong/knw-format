"""
knw_format.document
Core KnwDocument class — read, write, and validate .knw files.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .ontology import OntologyGraph, OntologyNode
from .memory import MemoryLayer


SPEC_VERSION = "knw/1.0"


class KnwDocument:
    """
    Represents a single .knw file.

    A .knw file is a UTF-8 encoded JSON document with five fields:
      - format     : spec version string
      - id         : unique document identifier
      - content    : full document text (Markdown)
      - ontology   : map of term keys to OntologyNode objects
      - embeddings : float vector of document meaning
      - memory     : personal reading history (local, not shared)
    """

    def __init__(
        self,
        id: str,
        content: str,
        ontology: Optional[dict] = None,
        embeddings: Optional[list] = None,
        memory: Optional[MemoryLayer] = None,
        format: str = SPEC_VERSION,
    ):
        self.format = format
        self.id = id
        self.content = content
        self.ontology = OntologyGraph(ontology or {})
        self.embeddings = embeddings or []
        self.memory = memory or MemoryLayer()

    # ── I/O ──────────────────────────────────────────────────────────────────

    @classmethod
    def load(cls, path: str | Path) -> "KnwDocument":
        """Load a .knw file from disk."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if path.suffix != ".knw":
            raise ValueError(f"Expected .knw file, got: {path.suffix}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cls._validate_raw(data)
        return cls._from_dict(data)

    def save(self, path: str | Path, strip_memory: bool = False) -> None:
        """
        Save document to disk.

        Args:
            path:         Output path. Should end in .ai
            strip_memory: If True, omit the memory field (use when sharing)
        """
        path = Path(path)
        data = self._to_dict(strip_memory=strip_memory)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def share(self, path: str | Path) -> None:
        """Save a shareable version with memory stripped."""
        self.save(path, strip_memory=True)

    # ── Serialisation ─────────────────────────────────────────────────────────

    def _to_dict(self, strip_memory: bool = False) -> dict:
        data = {
            "format": self.format,
            "id": self.id,
            "content": self.content,
            "ontology": self.ontology.to_dict(),
            "embeddings": self.embeddings,
        }
        if not strip_memory and self.memory:
            data["memory"] = self.memory.to_dict()
        return data

    @classmethod
    def _from_dict(cls, data: dict) -> "KnwDocument":
        ontology_raw = {
            k: OntologyNode(**v) for k, v in data.get("ontology", {}).items()
        }
        memory = MemoryLayer.from_dict(data["memory"]) if "memory" in data else MemoryLayer()
        return cls(
            format=data["format"],
            id=data["id"],
            content=data["content"],
            ontology=ontology_raw,
            embeddings=data.get("embeddings", []),
            memory=memory,
        )

    # ── Validation ────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_raw(data: dict) -> None:
        """Validate raw JSON dict against spec requirements."""
        required = ["format", "id", "content", "ontology", "embeddings"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: '{field}'")

        if data["format"] != SPEC_VERSION:
            raise ValueError(
                f"Unsupported format version: '{data['format']}'. "
                f"This parser supports '{SPEC_VERSION}'."
            )

        if not data["id"] or not isinstance(data["id"], str):
            raise ValueError("'id' must be a non-empty string.")

        import re
        if not re.match(r"^[a-z0-9\-]+$", data["id"]):
            raise ValueError(
                f"'id' must be lowercase kebab-case (a-z, 0-9, hyphens only). Got: '{data['id']}'"
            )

        if not data["content"] or not isinstance(data["content"], str):
            raise ValueError("'content' must be a non-empty string.")

        if not isinstance(data["ontology"], dict):
            raise ValueError("'ontology' must be an object.")

        if not isinstance(data["embeddings"], list):
            raise ValueError("'embeddings' must be an array.")

    # ── Utilities ─────────────────────────────────────────────────────────────

    def to_json(self, strip_memory: bool = False) -> str:
        """Return the document as a formatted JSON string."""
        return json.dumps(self._to_dict(strip_memory=strip_memory), indent=2, ensure_ascii=False)

    def word_count(self) -> int:
        return len(self.content.split())

    def ontology_density(self) -> float:
        """Ratio of ontology nodes to document words. Spec recommends >= 1 per 200 words."""
        wc = self.word_count()
        return len(self.ontology.nodes) / wc if wc > 0 else 0.0

    def __repr__(self) -> str:
        return (
            f"KnwDocument(id='{self.id}', "
            f"words={self.word_count()}, "
            f"ontology_nodes={len(self.ontology.nodes)}, "
            f"embeddings_dim={len(self.embeddings)})"
        )
