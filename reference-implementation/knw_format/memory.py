"""
knw_format.memory
MemoryLayer and DeltaEngine — the personal reading history of a .knw file.

The memory layer is populated by the READER APPLICATION, not the author.
It is personal data. It MUST be stripped before sharing a file.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


VALID_DELTA_TYPES = {"contradiction", "extension", "reference", "update"}


@dataclass
class DeltaItem:
    """
    A detected relationship between this document and another in the vault.

    Types:
      contradiction — this document asserts something that conflicts with another
      extension     — this document builds on or extends ideas in another
      reference     — this document cites or references another
      update        — this document supersedes or updates another
    """
    type: str
    file: str
    note: str
    resolved: bool = False

    def __post_init__(self):
        if self.type not in VALID_DELTA_TYPES:
            raise ValueError(
                f"Invalid delta type: '{self.type}'. "
                f"Must be one of: {sorted(VALID_DELTA_TYPES)}"
            )

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "file": self.file,
            "note": self.note,
            "resolved": self.resolved,
        }


class MemoryLayer:
    """
    Personal reading history for a .knw document.

    This object is maintained by the reader application. When the user
    opens a .knw file, the reader:
      1. Updates last_read and read_count
      2. Scans the vault for shared ontology nodes → updates linked_files
      3. Runs contradiction detection → updates delta

    This data never leaves the reader's local vault unless explicitly exported.
    """

    def __init__(
        self,
        created: Optional[str] = None,
        last_read: Optional[str] = None,
        read_count: int = 0,
        linked_files: Optional[list] = None,
        delta: Optional[list] = None,
    ):
        now = datetime.now(timezone.utc).isoformat()
        self.created = created or now
        self.last_read = last_read or now
        self.read_count = read_count
        self.linked_files: list[str] = linked_files or []
        self.delta: list[DeltaItem] = []

        for item in (delta or []):
            if isinstance(item, DeltaItem):
                self.delta.append(item)
            elif isinstance(item, dict):
                self.delta.append(DeltaItem(**item))

    def record_read(self) -> None:
        """Call this whenever the document is opened."""
        self.last_read = datetime.now(timezone.utc).isoformat()
        self.read_count += 1

    def add_link(self, file_id: str) -> None:
        """Add a cross-file link if not already present."""
        if file_id not in self.linked_files:
            self.linked_files.append(file_id)

    def add_delta(self, type: str, file: str, note: str) -> None:
        """Record a detected relationship with another file."""
        existing = [(d.type, d.file) for d in self.delta]
        if (type, file) not in existing:
            self.delta.append(DeltaItem(type=type, file=file, note=note))

    def resolve_delta(self, file: str, type: str) -> None:
        """Mark a delta as resolved (user has acknowledged it)."""
        for item in self.delta:
            if item.file == file and item.type == type:
                item.resolved = True

    def unresolved_deltas(self) -> list[DeltaItem]:
        return [d for d in self.delta if not d.resolved]

    def to_dict(self) -> dict:
        return {
            "created": self.created,
            "last_read": self.last_read,
            "read_count": self.read_count,
            "linked_files": self.linked_files,
            "delta": [d.to_dict() for d in self.delta],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryLayer":
        return cls(
            created=data.get("created"),
            last_read=data.get("last_read"),
            read_count=data.get("read_count", 0),
            linked_files=data.get("linked_files", []),
            delta=data.get("delta", []),
        )

    def __repr__(self) -> str:
        return (
            f"MemoryLayer(read_count={self.read_count}, "
            f"links={len(self.linked_files)}, "
            f"deltas={len(self.delta)})"
        )
