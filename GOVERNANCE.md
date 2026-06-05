# Governance

The `.knw` format is an open specification. This document explains how decisions are made.

---

## Principles

**The spec serves users, not implementers.** Decisions prioritise the interests of people who read and write documents over the interests of companies building products on top of the format.

**No single owner.** No company or individual controls the spec. The original author has no special veto power over future versions.

**Consensus over voting.** We seek rough consensus. Formal votes are a last resort.

**Stability over features.** Once a version is stable, it is frozen. New features go into the next minor version. The upgrade path must always be clear.

---

## Decision types

**Editorial changes** (typos, clarifications, examples)
Anyone can open a PR. Merged with one approval.

**Additive changes** (new optional fields, new ontology types, new relation types)
Requires an open issue with 7-day comment period. Merged with two approvals, no unresolved objections.

**Breaking changes** (anything that invalidates existing knw/1.0 files)
Requires an open issue with 30-day comment period. Requires consensus from at least three independent implementers. Results in a major version bump (ai/2.0).

---

## Roles

**Contributors** — anyone who opens a PR or issue
**Reviewers** — contributors with a track record of thoughtful feedback; can approve PRs
**Maintainers** — responsible for releases and final merge decisions

New maintainers are nominated by existing maintainers and confirmed by community consensus.

The current maintainer list is in `MAINTAINERS.md`.

---

## If this project is abandoned

If the original maintainers become inactive for more than 12 months, any contributor may fork the repository and continue development under the same MIT license. The spec itself is CC0 — it belongs to everyone.
