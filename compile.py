#!/usr/bin/env python3
"""compile.py

CLI to compile a Markdown file into a .knw document using the reference implementation.

Usage:
  python compile.py path/to/file.md
"""
import argparse
import os
import re
import sys
from pathlib import Path


def slugify(name: str) -> str:
    name = name.lower()
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"[^a-z0-9\-]", "", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-") or "document"


def main():
    parser = argparse.ArgumentParser(description="Compile a Markdown file to .knw using Ollama backend")
    parser.add_argument("input", help="Path to input Markdown file")
    parser.add_argument("--output-dir", default="examples", help="Directory to write the resulting .knw file")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        sys.exit(2)

    content = input_path.read_text(encoding="utf-8")
    # Derive id from filename
    id_base = slugify(input_path.stem)

    # Ensure reference-implementation package is importable
    base = Path(__file__).parent.resolve()
    ref_impl = base / "reference-implementation"
    if str(ref_impl) not in sys.path:
        sys.path.insert(0, str(ref_impl))

    try:
        from knw_format.generate import generate_document
    except Exception as exc:
        print("Failed to import reference implementation. Ensure reference-implementation/ is present.")
        raise

    print(f"Compiling '{input_path}' → id='{id_base}' using ollama backend...")
    doc = generate_document(id=id_base, content=content, backend="ollama")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{id_base}.knw"
    try:
        doc.save(out_path)
    except Exception as exc:
        print(f"Failed to save .knw file: {exc}")
        raise

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
