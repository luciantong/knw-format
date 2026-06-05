"""
Tests for the .knw format reference implementation.
Run with: pytest tests/
"""

import json
import tempfile
from pathlib import Path

import pytest

from knw_format import KnwDocument, OntologyNode, OntologyGraph, MemoryLayer, DeltaItem
from knw_format.embeddings import StubEmbeddingBackend


# ── Fixtures ──────────────────────────────────────────────────────────────────

MINIMAL_DOC = {
    "format": "knw/1.0",
    "id": "test-document",
    "content": "# Test\n\nThis is a test document.",
    "ontology": {
        "test": {
            "type": "concept",
            "relation": "references",
            "target": "document",
            "definition": "A test concept."
        }
    },
    "embeddings": [0.1, 0.2, 0.3]
}


@pytest.fixture
def minimal_doc():
    return KnwDocument(
        id="test-document",
        content="# Test\n\nThis is a test document about payments infrastructure.",
        ontology={
            "payments": OntologyNode(
                type="concept",
                relation="enables",
                target="commerce",
                definition="Systems that move money between parties."
            )
        },
        embeddings=[0.1, 0.2, 0.3],
    )


# ── Document tests ─────────────────────────────────────────────────────────────

class TestKnwDocument:

    def test_creates_valid_document(self, minimal_doc):
        assert minimal_doc.id == "test-document"
        assert "payments" in minimal_doc.ontology
        assert minimal_doc.embeddings == [0.1, 0.2, 0.3]

    def test_save_and_load_roundtrip(self, minimal_doc):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.knw"
            minimal_doc.save(path)
            loaded = KnwDocument.load(path)

            assert loaded.id == minimal_doc.id
            assert loaded.content == minimal_doc.content
            assert loaded.embeddings == minimal_doc.embeddings
            assert "payments" in loaded.ontology

    def test_save_strips_memory_when_sharing(self, minimal_doc):
        minimal_doc.memory.record_read()
        minimal_doc.memory.add_link("other-document")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "shared.knw"
            minimal_doc.share(path)

            with open(path) as f:
                raw = json.load(f)

            assert "memory" not in raw

    def test_load_rejects_wrong_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrong.json"
            path.write_text("{}")
            with pytest.raises(ValueError, match="Expected .knw file"):
                KnwDocument.load(path)

    def test_load_rejects_missing_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.knw"
            path.write_text(json.dumps({"format": "knw/1.0"}))
            with pytest.raises(ValueError, match="Missing required field"):
                KnwDocument.load(path)

    def test_load_rejects_wrong_format_version(self):
        bad = {**MINIMAL_DOC, "format": "knw/99.0"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.knw"
            path.write_text(json.dumps(bad))
            with pytest.raises(ValueError, match="Unsupported format version"):
                KnwDocument.load(path)

    def test_load_rejects_invalid_id(self):
        bad = {**MINIMAL_DOC, "id": "Invalid ID With Spaces!"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.knw"
            path.write_text(json.dumps(bad))
            with pytest.raises(ValueError, match="lowercase kebab-case"):
                KnwDocument.load(path)

    def test_word_count(self, minimal_doc):
        assert minimal_doc.word_count() > 0

    def test_ontology_density(self, minimal_doc):
        density = minimal_doc.ontology_density()
        assert density > 0

    def test_to_json_is_valid_json(self, minimal_doc):
        j = minimal_doc.to_json()
        parsed = json.loads(j)
        assert parsed["id"] == "test-document"


# ── Ontology tests ─────────────────────────────────────────────────────────────

class TestOntologyNode:

    def test_valid_node(self):
        node = OntologyNode(
            type="entity",
            relation="isA",
            target="company",
            definition="A test company."
        )
        assert node.type == "entity"
        assert node.relation == "isA"

    def test_rejects_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid ontology type"):
            OntologyNode(type="invalid", relation="isA", target="x", definition="x")

    def test_rejects_invalid_relation(self):
        with pytest.raises(ValueError, match="Invalid relation type"):
            OntologyNode(type="entity", relation="banana", target="x", definition="x")

    def test_to_dict_roundtrip(self):
        node = OntologyNode(
            type="method",
            relation="quantifies",
            target="value",
            definition="A valuation method.",
            aliases=["valuation", "dcf"]
        )
        d = node.to_dict()
        restored = OntologyNode(**d)
        assert restored.type == node.type
        assert restored.aliases == node.aliases


class TestOntologyGraph:

    def test_by_type(self):
        graph = OntologyGraph({
            "nuvei": OntologyNode(type="entity", relation="isA", target="company", definition="A company."),
            "dcf": OntologyNode(type="method", relation="quantifies", target="value", definition="A method."),
        })
        entities = graph.by_type("entity")
        assert "nuvei" in entities
        assert "dcf" not in entities

    def test_shared_nodes(self):
        g1 = OntologyGraph({
            "payments": OntologyNode(type="concept", relation="enables", target="commerce", definition="x"),
            "nuvei": OntologyNode(type="entity", relation="isA", target="company", definition="x"),
        })
        g2 = OntologyGraph({
            "payments": OntologyNode(type="concept", relation="enables", target="commerce", definition="y"),
            "stripe": OntologyNode(type="entity", relation="isA", target="company", definition="y"),
        })
        shared = g1.shared_nodes(g2)
        assert shared == {"payments"}


# ── Memory tests ──────────────────────────────────────────────────────────────

class TestMemoryLayer:

    def test_record_read_increments_count(self):
        mem = MemoryLayer()
        assert mem.read_count == 0
        mem.record_read()
        assert mem.read_count == 1

    def test_add_link_deduplicates(self):
        mem = MemoryLayer()
        mem.add_link("file-a")
        mem.add_link("file-a")
        assert mem.linked_files.count("file-a") == 1

    def test_add_delta(self):
        mem = MemoryLayer()
        mem.add_delta("contradiction", "other-doc", "Disagrees on growth rate.")
        assert len(mem.delta) == 1
        assert mem.delta[0].type == "contradiction"

    def test_resolve_delta(self):
        mem = MemoryLayer()
        mem.add_delta("contradiction", "other-doc", "Disagrees.")
        mem.resolve_delta("other-doc", "contradiction")
        assert mem.delta[0].resolved is True

    def test_unresolved_deltas(self):
        mem = MemoryLayer()
        mem.add_delta("contradiction", "file-a", "Note A.")
        mem.add_delta("extension", "file-b", "Note B.")
        mem.resolve_delta("file-a", "contradiction")
        unresolved = mem.unresolved_deltas()
        assert len(unresolved) == 1
        assert unresolved[0].file == "file-b"

    def test_roundtrip_serialisation(self):
        mem = MemoryLayer()
        mem.record_read()
        mem.add_link("linked-file")
        mem.add_delta("reference", "cited-file", "Cited here.")
        restored = MemoryLayer.from_dict(mem.to_dict())
        assert restored.read_count == mem.read_count
        assert restored.linked_files == mem.linked_files
        assert len(restored.delta) == 1
