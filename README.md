# .knw — The Open Intelligent Document Format

> *PDF made documents portable. .knw makes them alive.*

**Version:** 0.1.0 (Draft)
**Status:** Open for community review
**License:** MIT (spec + tooling) — free forever

---

## What is this?

`.knw` is an open file format specification for intelligent documents — documents that carry semantic meaning, ontological relationships, and personal memory alongside their content.

A `.knw` file is not an app. It is not a chatbot. It is a document — readable as plain text, portable across any system, and renderable by any application that implements the spec.

The difference between a `.knw` file and a PDF:

| | PDF | .ai |
|---|---|---|
| Portable | ✓ | ✓ |
| Human readable | ✓ | ✓ |
| Semantically structured | ✗ | ✓ |
| Carries ontological relationships | ✗ | ✓ |
| Supports personal memory layer | ✗ | ✓ |
| Adapts to who is reading | ✗ | ✓ |
| Open standard | ✓ | ✓ |

---

## The core idea

When you open a PDF, it is dead. It is the same document for everyone, every time.

When a `.knw` file is rendered, it is aware of:
- **What it contains** — structured as a knowledge graph, not flat text
- **What it connects to** — ontological relationships between concepts across your entire document vault
- **What has changed** — a memory layer that tracks how your thinking has evolved

This is not AI magic. It is a well-defined schema that any application can implement. The intelligence comes from the structure, not from a black box.

---

## The file format

A `.knw` file is a UTF-8 encoded JSON document with five required fields.

```json
{
  "format": "knw/1.0",
  "id": "unique-document-identifier",
  "content": "The full document text in Markdown.",
  "ontology": {
    "term-key": {
      "type": "concept | entity | method | relation",
      "relation": "isA | enables | opposes | quantifies | correlates | causes | requires",
      "target": "target-concept-key",
      "definition": "Human-readable definition of this term in this document's context."
    }
  },
  "embeddings": [0.231, 0.847, 0.102],
  "memory": {
    "created": "ISO-8601 date",
    "last_read": "ISO-8601 date",
    "linked_files": ["file-id-1", "file-id-2"],
    "delta": [
      {
        "type": "contradiction | extension | reference",
        "file": "file-id",
        "note": "Human-readable description of the relationship."
      }
    ]
  }
}
```

See [`spec/SPEC.md`](spec/SPEC.md) for the full specification.

---

## Why ontology?

Ontologies are formal representations of knowledge — they define not just *what* things are but *how they relate* to each other. A concept tagged `isA → payments-platform` is machine-readable in a way that a keyword tag is not.

This means:
- Two documents that both reference "DCF" but in different contexts can be distinguished
- A renderer can surface connections across documents based on *relationship type*, not just keyword overlap
- The format is interoperable — any application implementing the spec will parse ontology nodes the same way

The `.knw` format borrows from established ontology standards (OWL, RDF) but uses a deliberately minimal subset that any developer can implement without a PhD.

---

## Quick start

### Reading a .knw file

```python
from knw_format import KnwDocument

doc = KnwDocument.load("my-document.ai")

print(doc.content)           # raw markdown text
print(doc.ontology.nodes)    # list of ontological concepts
print(doc.memory.delta)      # what has changed since last read
```

### Creating a .knw file

```python
from knw_format import KnwDocument, OntologyNode

doc = KnwDocument(
    id="my-first-doc",
    content="# My Document\n\nThis is about **payments infrastructure**.",
    ontology={
        "payments-infrastructure": OntologyNode(
            type="concept",
            relation="enables",
            target="commerce",
            definition="The rails and APIs that move money between parties."
        )
    }
)

doc.save("my-document.ai")
```

### Generating ontology automatically

```python
from knw_format.generate import extract_ontology

content = "Nuvei is a payments platform that processed $203B in volume."
ontology = extract_ontology(content, backend="ollama")  # uses local Ollama at http://127.0.0.1:11434 by default

# Required environment variables for Ollama:
#   OLLAMA_URL=http://127.0.0.1:11434
#   OLLAMA_MODEL=your-installed-model-name (for example: llama2:latest)
# Example:
#   export OLLAMA_MODEL=llama2:latest
```

See [`reference-implementation/`](reference-implementation/) for full usage.

---

## Repository structure

```
knw-format/
├── README.md                        # this file
├── LICENSE                          # MIT
├── CONTRIBUTING.md                  # how to contribute
├── GOVERNANCE.md                    # how decisions are made
│
├── spec/
│   ├── SPEC.md                      # full format specification
│   ├── ONTOLOGY_TYPES.md            # valid ontology types and relations
│   └── CHANGELOG.md                 # version history
│
├── reference-implementation/
│   ├── README.md
│   ├── requirements.txt
│   ├── knw_format/
│   │   ├── __init__.py
│   │   ├── document.py              # KnwDocument class
│   │   ├── ontology.py              # OntologyNode, OntologyGraph
│   │   ├── memory.py                # MemoryLayer, DeltaEngine
│   │   ├── embeddings.py            # embedding generation (pluggable)
│   │   └── generate.py              # auto-extract ontology from text
│   └── tests/
│       ├── test_document.py
│       ├── test_ontology.py
│       └── test_memory.py
│
└── examples/
    ├── simple.ai                    # minimal valid .knw file
    ├── investment-thesis.ai         # finance/research example
    └── lecture-notes.ai             # academic example
```

---

## Principles

**1. The spec is the product.** The format belongs to everyone. No company owns it.

**2. Renderers are separate from the format.** A `.knw` file is readable in a text editor. How it is *displayed* is up to the application, not the spec.

**3. The memory layer is personal and local.** The `memory` field is populated by the reader application, not baked into the file at creation. When you share a `.knw` file, you share the content and ontology — not your personal reading history.

**4. Minimal by default.** The spec defines the minimum viable schema. Extensions are allowed but must be namespaced to avoid conflicts.

**5. Backwards compatible forever.** Any valid `knw/1.0` file will be readable by any future version of the spec.

---

## Status and roadmap

This is a draft specification. It is open for community review and comment.

- [x] v0.1 — Core schema (format, content, ontology, embeddings, memory)
- [ ] v0.2 — Ontology validation rules and relation taxonomy
- [ ] v0.3 — Cross-file linking protocol
- [ ] v0.4 — Renderer interface specification
- [ ] v1.0 — Stable, frozen specification

---

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md). The most valuable contributions right now are:

- Feedback on the ontology type system — are these the right relation types?
- Edge cases in the schema — what breaks?
- Alternative implementations in other languages (JS, Go, Rust)
- Real-world `.knw` files that stress-test the format

---

## Who made this

This specification was initiated by Lucian Tong. It is not owned by any company. It is dedicated to the public domain of ideas.

*"The goal is a document format that makes humans smarter over time — not just informed in the moment."*

---

## License

MIT. Do whatever you want with it. Build on it. Compete with it. Improve it. Just keep the spec open.
