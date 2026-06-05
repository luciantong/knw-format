"""
knw_format.ontology
OntologyNode and OntologyGraph — the semantic knowledge layer of a .knw file.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


VALID_TYPES = {"concept", "entity", "method", "relation", "event", "metric"}

VALID_RELATIONS = {
    "isA", "enables", "opposes", "quantifies", "causes",
    "requires", "correlates", "partOf", "references"
}


@dataclass
class OntologyNode:
    """
    A single node in the document's ontology graph.

    Represents a term or concept that appears in the document,
    its type, how it relates to another concept, and a definition
    grounded in this document's context.
    """
    type: str
    relation: str
    target: str
    definition: str
    aliases: list = field(default_factory=list)
    external: Optional[str] = None

    def __post_init__(self):
        if self.type not in VALID_TYPES:
            raise ValueError(
                f"Invalid ontology type: '{self.type}'. "
                f"Must be one of: {sorted(VALID_TYPES)}"
            )
        if self.relation not in VALID_RELATIONS:
            raise ValueError(
                f"Invalid relation type: '{self.relation}'. "
                f"Must be one of: {sorted(VALID_RELATIONS)}"
            )

    def to_dict(self) -> dict:
        d = {
            "type": self.type,
            "relation": self.relation,
            "target": self.target,
            "definition": self.definition,
        }
        if self.aliases:
            d["aliases"] = self.aliases
        if self.external:
            d["external"] = self.external
        return d

    def __repr__(self) -> str:
        return f"OntologyNode({self.type}: {self.relation} → {self.target})"


class OntologyGraph:
    """
    The full ontology of a .knw document.

    A dict-like container of OntologyNode objects, keyed by term.
    Supports querying by type, relation, and target.
    """

    def __init__(self, nodes: dict):
        self.nodes: dict[str, OntologyNode] = {}
        for key, value in nodes.items():
            if isinstance(value, OntologyNode):
                self.nodes[key] = value
            elif isinstance(value, dict):
                self.nodes[key] = OntologyNode(**value)
            else:
                raise TypeError(f"Expected OntologyNode or dict for key '{key}', got {type(value)}")

    def by_type(self, type: str) -> dict[str, OntologyNode]:
        """Return all nodes of a given type."""
        return {k: v for k, v in self.nodes.items() if v.type == type}

    def by_relation(self, relation: str) -> dict[str, OntologyNode]:
        """Return all nodes with a given relation."""
        return {k: v for k, v in self.nodes.items() if v.relation == relation}

    def targets_of(self, target: str) -> dict[str, OntologyNode]:
        """Return all nodes that point to a given target concept."""
        return {k: v for k, v in self.nodes.items() if v.target == target}

    def shared_nodes(self, other: "OntologyGraph") -> set[str]:
        """
        Return keys that appear in both ontology graphs.
        Used by the memory layer to detect cross-file links.
        """
        return set(self.nodes.keys()) & set(other.nodes.keys())

    def to_dict(self) -> dict:
        return {k: v.to_dict() for k, v in self.nodes.items()}

    def __len__(self) -> int:
        return len(self.nodes)

    def __contains__(self, key: str) -> bool:
        return key in self.nodes

    def __getitem__(self, key: str) -> OntologyNode:
        return self.nodes[key]

    def __repr__(self) -> str:
        return f"OntologyGraph({len(self.nodes)} nodes)"
