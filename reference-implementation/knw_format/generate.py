"""
knw_format.generate
Auto-extract ontology nodes and embeddings from plain text.

This module is optional — .knw files can be authored by hand.
Use this when converting existing documents to .knw format.
"""

import json
import re
import uuid
from typing import Optional

from .ontology import OntologyNode
from .embeddings import EmbeddingBackend, get_default_backend


EXTRACTION_PROMPT = """You are an ontology extraction engine. Given a document, extract the most important concepts, entities, methods, and relationships.

Return ONLY a JSON object (no markdown, no explanation) where:
- Each key is a short, lowercase, hyphenated identifier for the concept (e.g. "payments-infrastructure", "dcf-valuation")
- Each value has: type, relation, target, definition

Valid types: concept, entity, method, relation, event, metric
Valid relations: isA, enables, opposes, quantifies, causes, requires, correlates, partOf, references

Extract 3-8 nodes. Focus on the most semantically important terms.

Document:
---
{content}
---

Return JSON only:"""


def extract_ontology(
    content: str,
    backend: str = "ollama",
    api_key: Optional[str] = None,
    max_nodes: int = 8,
) -> dict[str, OntologyNode]:
    """
    Extract ontology nodes from document content using an LLM.

    Args:
        content:  Document text (Markdown)
        backend:  'anthropic' | 'openai' | 'ollama' | 'stub'
        api_key:  API key (reads from env if not provided)
        max_nodes: Maximum number of nodes to extract

    Returns:
        Dict of term keys to OntologyNode objects
    """
    if backend == "stub":
        return _stub_ontology(content)

    prompt = EXTRACTION_PROMPT.format(content=content[:4000])

    if backend == "anthropic":
        raw = _call_anthropic(prompt, api_key)
    elif backend == "openai":
        raw = _call_openai(prompt, api_key)
    elif backend == "ollama":
        raw = _call_ollama(prompt, api_key)
    else:
        raise ValueError(f"Unknown backend: '{backend}'. Use 'anthropic', 'openai', 'ollama', or 'stub'.")

    return _parse_ontology_response(raw, max_nodes)


def generate_document(
    id: str,
    content: str,
    backend: str = "ollama",
    api_key: Optional[str] = None,
    embedding_backend: Optional[EmbeddingBackend] = None,
) -> dict:
    """
    Generate a complete .knw file dict from raw content.
    Extracts ontology and computes embeddings automatically.

    Returns a dict ready to be saved as a .knw file.
    """
    from .document import KnwDocument

    ontology = extract_ontology(content, backend=backend, api_key=api_key)
    emb_backend = embedding_backend or get_default_backend()
    embeddings = emb_backend.embed(content)

    return KnwDocument(
        id=id,
        content=content,
        ontology=ontology,
        embeddings=embeddings,
    )


# ── LLM backends ─────────────────────────────────────────────────────────────

def _call_anthropic(prompt: str, api_key: Optional[str]) -> str:
    import os
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package required: pip install anthropic")

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_openai(prompt: str, api_key: Optional[str]) -> str:
    import os
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package required: pip install openai")

    key = api_key or os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def _call_ollama(prompt: str, api_key: Optional[str]) -> str:
    import json
    import os
    try:
        import requests
    except ImportError:
        raise ImportError("requests package required: pip install requests")

    # Use the local Ollama HTTP API endpoint for the new generation API
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
    model = os.environ.get("OLLAMA_MODEL", "llama3")

    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 1024,
        "temperature": 0.2,
    }

    try:
        resp = requests.post(ollama_url, json=payload, timeout=30)
    except Exception as exc:
        raise RuntimeError(f"Unable to reach Ollama at {ollama_url}: {exc}") from exc

    if resp.status_code != 200:
        # try to include any message from the service
        text = resp.text
        raise RuntimeError(f"Ollama request failed ({resp.status_code}): {text}")

    try:
        data = resp.json()
    except Exception:
        # If the service returned plain text, return it directly
        return resp.text or ""

    # The new Ollama generation API may return either a top-level text or a choices array.
    # Normalize to a string payload that contains the model's output (JSON string expected).
    if isinstance(data, dict):
        # common shapes: {"text": "..."} or {"choices": [{"content": ...}]}
        if "text" in data and isinstance(data["text"], str):
            return data["text"]
        if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
            choice = data["choices"][0]
            # content may be a dict (already-parsed JSON) or a string
            content = choice.get("content") or choice.get("text") or choice.get("message")
            if isinstance(content, (dict, list)):
                return json.dumps(content)
            if isinstance(content, str):
                return content
        # fallback: return the whole JSON document as string
        return json.dumps(data)

    # If data is a list or other type, stringify it
    return json.dumps(data)


def _ollama_list_models(ollama_url: str) -> list[str]:
    import json
    import urllib.error
    import urllib.parse
    import urllib.request

    endpoint = urllib.parse.urljoin(ollama_url.rstrip("/"), "/v1/models")
    request = urllib.request.Request(
        endpoint,
        headers={"Content-Type": "application/json"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except Exception:
        return []

    data = json.loads(raw)
    if not isinstance(data, dict):
        return []

    models = data.get("models") or data.get("model") or []
    if isinstance(models, list):
        return [m.get("name") if isinstance(m, dict) else str(m) for m in models]
    return []


def _parse_ontology_response(raw: str, max_nodes: int) -> dict[str, OntologyNode]:
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"```$", "", raw)

    data = json.loads(raw)
    nodes = {}
    for i, (key, val) in enumerate(data.items()):
        if i >= max_nodes:
            break
        try:
            nodes[key] = OntologyNode(**val)
        except (TypeError, ValueError):
            continue
    return nodes


def _stub_ontology(content: str) -> dict[str, OntologyNode]:
    """Minimal stub for testing — extracts nothing meaningful."""
    return {
        "document": OntologyNode(
            type="concept",
            relation="references",
            target="knowledge",
            definition="Stub ontology node generated without LLM."
        )
    }
