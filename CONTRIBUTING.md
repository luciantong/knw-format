# Contributing to the .knw format

Thank you for your interest. This is an open specification — contributions from everyone are welcome.

---

## What we need most right now

**Feedback on the spec (most valuable)**
Open an issue with the label `spec-feedback`. The most useful contributions are:
- Edge cases that the current schema cannot represent
- Ontology types or relation types that are missing
- Real-world documents that expose limitations
- Comparison to existing standards (OWL, RDF, JSON-LD, DocLang)

**Alternative implementations**
The reference implementation is Python. Implementations in other languages are highly valuable. If you build one, open a PR to add it to the README's implementation list. Any language. Any license (must be open source).

**Example .knw files**
Add real-world `.knw` files to `examples/`. These stress-test the format and help new users understand what good ontology looks like in practice. Domains we want more of:
- Academic research papers
- Legal documents
- Medical literature
- Technical documentation
- Historical texts

**Validator**
A standalone validator that checks a `.knw` file against the spec would be enormously useful. This could be a CLI tool, a web validator, or a GitHub Action.

---

## How to contribute code

1. Fork the repository
2. Create a branch: `git checkout -b your-feature-name`
3. Make your changes
4. Run the tests: `cd reference-implementation && pytest`
5. Open a pull request with a clear description of what you changed and why

**Code style:** PEP 8. Type hints everywhere. Docstrings on all public methods.

---

## How to propose spec changes

Spec changes are more significant than code changes. To propose a change to `spec/SPEC.md`:

1. Open an issue first, labelled `spec-proposal`
2. Describe the problem you are trying to solve, not just the solution
3. Show a concrete example of a `.knw` file that requires the change
4. Allow at least 14 days for community discussion before a PR is opened

Breaking changes (anything that invalidates existing `knw/1.0` files) require consensus from at least three independent implementers.

---

## What we will not accept

- Changes that require a specific embedding model or LLM provider
- Changes that make the memory layer non-local (i.e. embedded in shared files by default)
- Changes that add proprietary or patented elements to the core spec
- Anything that makes a valid `.knw` file non-human-readable in a text editor

---

## Code of conduct

Be direct. Disagree openly. Assume good faith. No personal attacks.

The spec exists to serve users of documents — students, researchers, writers, analysts. Keep that in mind in every discussion.
