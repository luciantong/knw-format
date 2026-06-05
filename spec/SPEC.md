# .knw Format Specification

**Version:** 0.1.0
**Status:** Draft — open for community review
**Date:** June 2026

---

## 1. Overview

The `.knw` format is an open specification for intelligent documents. A `.knw` file is a UTF-8 encoded JSON document that contains document content alongside structured semantic metadata: an ontology of concepts and their relationships, a vector embedding of the document's meaning, and a memory layer tracking how the document relates to a reader's broader knowledge.

The format is designed to be:
- **Human readable** — plain JSON, viewable in any text editor
- **Machine parseable** — strict schema, no ambiguity
- **Renderer agnostic** — the spec defines structure, not presentation
- **Privacy respecting** — the memory layer is personal and local; it is not part of the shared file

---

## 2. File structure

A valid `.knw` file MUST contain the following top-level fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `format` | string | ✓ | Always `"knw/1.0"` for this version |
| `id` | string | ✓ | Unique document identifier (kebab-case, URL-safe) |
| `content` | string | ✓ | Full document text in Markdown |
| `ontology` | object | ✓ | Map of term keys to OntologyNode objects |
| `embeddings` | array | ✓ | Float array — vector embedding of `content` |
| `memory` | object | ✗ | Personal memory layer (populated by reader, not author) |

---

## 3. Field definitions

### 3.1 `format`

```json
"format": "knw/1.0"
```

MUST be the string `"knw/1.0"` for documents conforming to this version. Future versions will increment the minor or major number. Parsers MUST reject documents with unrecognised format strings unless in permissive mode.

---

### 3.2 `id`

```json
"id": "nuvei-investment-thesis"
```

A unique, human-readable identifier for this document. MUST be:
- Lowercase
- Kebab-case (hyphens, no spaces)
- URL-safe (no special characters)
- Unique within a vault (collection of `.knw` files)

---

### 3.3 `content`

```json
"content": "# Nuvei Investment Thesis\n\nNuvei is a payments platform..."
```

The full document text, encoded as a Markdown string. Renderers MUST display this as the primary document content. All whitespace and newlines MUST be preserved.

---

### 3.4 `ontology`

The ontology is a map of string keys to OntologyNode objects. Each key represents a term or concept that appears in or is relevant to the document.

```json
"ontology": {
  "nuvei": {
    "type": "entity",
    "relation": "isA",
    "target": "payments-platform",
    "definition": "Montreal-based global payments company. Founded 2003."
  },
  "dcf": {
    "type": "method",
    "relation": "quantifies",
    "target": "intrinsic-value",
    "definition": "Discounted Cash Flow valuation methodology."
  }
}
```

#### OntologyNode fields

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | ✓ | One of the valid ontology types (see Section 4) |
| `relation` | string | ✓ | One of the valid relation types (see Section 5) |
| `target` | string | ✓ | The key of the concept this node relates to |
| `definition` | string | ✓ | Human-readable definition in this document's context |
| `aliases` | array | ✗ | Alternative terms that map to this node |
| `external` | string | ✗ | URI to an external ontology (e.g. Wikidata QID) |

---

### 3.5 `embeddings`

```json
"embeddings": [0.231, -0.847, 0.102, 0.445, ...]
```

A float array representing the vector embedding of the document's `content`. This enables semantic similarity search across a vault of `.knw` files.

**Requirements:**
- MUST be a flat array of IEEE 754 floats
- Dimensionality MUST be consistent across all files in a vault
- The embedding model used SHOULD be recorded in the document's `meta` extension field
- Implementations MAY use any embedding model; the spec does not mandate a specific one

**Recommended models (as of v0.1):**
- `text-embedding-3-small` (OpenAI) — 1536 dimensions
- `nomic-embed-text` (Nomic, local) — 768 dimensions
- `mxbai-embed-large` (MixedBread, local) — 1024 dimensions

---

### 3.6 `memory`

The memory layer is populated by the **reader application**, not the document author. When a `.knw` file is shared, the memory field SHOULD be stripped or left empty. It is personal data belonging to the reader.

```json
"memory": {
  "created": "2026-06-04T10:30:00Z",
  "last_read": "2026-06-04T14:22:00Z",
  "read_count": 3,
  "linked_files": ["payments-sector-overview", "ca-cib-markets-research"],
  "delta": [
    {
      "type": "contradiction",
      "file": "payments-sector-overview",
      "note": "DCF terminal growth assumption differs (12% here vs 9% there)",
      "resolved": false
    }
  ]
}
```

#### Memory fields

| Field | Type | Description |
|---|---|---|
| `created` | ISO-8601 | When this file was first opened by this reader |
| `last_read` | ISO-8601 | Most recent read timestamp |
| `read_count` | integer | Number of times opened |
| `linked_files` | array | IDs of `.knw` files in the vault that share ontology nodes with this file |
| `delta` | array | List of DeltaItem objects (see below) |

#### DeltaItem fields

| Field | Type | Description |
|---|---|---|
| `type` | string | One of: `contradiction`, `extension`, `reference`, `update` |
| `file` | string | ID of the related file |
| `note` | string | Human-readable description of the relationship |
| `resolved` | boolean | Whether the reader has acknowledged this delta |

---

## 4. Ontology types

| Type | Description | Example |
|---|---|---|
| `concept` | An abstract idea or principle | "modular architecture", "market risk" |
| `entity` | A named real-world thing | "Nuvei Corporation", "Federal Reserve" |
| `method` | A process, technique, or procedure | "DCF valuation", "regression analysis" |
| `relation` | A relationship between two other nodes | "acquisition", "regulatory oversight" |
| `event` | A discrete occurrence in time | "Paya acquisition", "rate hike" |
| `metric` | A measurable quantity | "EBITDA margin", "total volume" |

---

## 5. Relation types

Relations define the directed edge between an ontology node and its target.

| Relation | Description | Example |
|---|---|---|
| `isA` | Subtype or instance of | `nuvei` isA `payments-platform` |
| `enables` | Makes possible or facilitates | `payments-infrastructure` enables `commerce` |
| `opposes` | Contradicts or competes with | `modular-platform` opposes `bundled-saas` |
| `quantifies` | Measures or assigns value to | `dcf` quantifies `intrinsic-value` |
| `causes` | Produces as a result | `rate-hike` causes `valuation-compression` |
| `requires` | Depends on as a prerequisite | `lbo` requires `leverage` |
| `correlates` | Statistically or causally associated | `gaming-revenue` correlates `regulatory-risk` |
| `partOf` | Component or subset of | `paya` partOf `nuvei` |
| `references` | Cites or points to | `thesis` references `annual-report` |

---

## 6. Extensions

Implementations MAY add custom fields using the `x-` prefix namespace:

```json
{
  "format": "knw/1.0",
  "x-author": "lucian.tong",
  "x-vault": "finance-research",
  "x-embedding-model": "text-embedding-3-small"
}
```

Extensions MUST NOT conflict with reserved top-level field names. Parsers MUST ignore unknown `x-` fields without error.

---

## 7. Validation rules

A conforming `.knw` file MUST:

1. Be valid JSON (RFC 8259)
2. Be encoded in UTF-8
3. Contain all required top-level fields
4. Have a `format` value of `"knw/1.0"`
5. Have an `id` that is lowercase, kebab-case, and URL-safe
6. Have a `content` field that is a non-empty string
7. Have an `ontology` where each node contains `type`, `relation`, `target`, and `definition`
8. Have `type` values from the defined type vocabulary (Section 4)
9. Have `relation` values from the defined relation vocabulary (Section 5)
10. Have `embeddings` as a flat array of floats

A conforming `.knw` file SHOULD:
- Include at least one ontology node per 200 words of content
- Use external ontology URIs where well-known entities are referenced
- Strip the `memory` field before sharing

---

## 8. Versioning

This specification follows semantic versioning.

- **Patch versions** (1.0.x) — clarifications and editorial fixes only
- **Minor versions** (1.x.0) — backwards-compatible additions
- **Major versions** (x.0.0) — breaking changes; require migration

All `ai/1.x` files MUST be parseable by any `knw/1.0` compliant reader.

---

## 9. Conformance

An implementation is **conforming** if it:

1. Can parse any valid `knw/1.0` file without error
2. Correctly exposes the `content`, `ontology`, and `embeddings` fields
3. Does not modify the `content` field during read/write cycles
4. Strips or isolates the `memory` field before file sharing operations

---

## Appendix A — Minimal valid example

```json
{
  "format": "knw/1.0",
  "id": "hello-world",
  "content": "# Hello World\n\nThis is a minimal valid .ai document.",
  "ontology": {
    "hello-world": {
      "type": "concept",
      "relation": "references",
      "target": "document",
      "definition": "A minimal example document for testing."
    }
  },
  "embeddings": [0.1, 0.2, 0.3]
}
```

---

## Appendix B — Change log

See [`CHANGELOG.md`](CHANGELOG.md).
