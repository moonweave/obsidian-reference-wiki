# Changelog

All notable public changes are recorded here. This project follows semantic
versioning for public releases.

## [Unreleased]

- Added a library tier so an existing paper corpus can join the schema in
  place: notes keep their basenames and legacy `status`, and carry
  `review_status` plus `summary_basis` so an abstract-derived summary can no
  longer pass for a reviewed reading. `check_notes.py` gains `--library-scope`
  and `--scope`, and skips dot-directories that Obsidian does not index.
  Contract version 15.

## [0.2.0] — 2026-08-10

- Added an Answer mode: the skill now reads its own notes back, quoting the
  recorded page anchor and evidence label, refusing unreviewed material as
  evidence, and never editing the Vault while answering. Contract version 14.
- Added an entry gate so every request that would create or change a Vault file
  resolves the Vault and checks for a `Reference Profile` first, whatever the
  user opened with. Onboarding now runs once per Vault instead of once per
  conversation, and a question skips the interview.
- Serialized external local file locations in frontmatter as percent-encoded
  `file:///` URIs so cloud-storage directory names containing `@` are no longer
  read as email links, with an explicit `Open canonical source` link in the
  dossier body. Legacy absolute paths remain readable.
- Published an install and usage guide page at `docs/guide.html`, covering
  Claude Code and Codex, and linked it from both READMEs.
- Reworked the English and Korean README pages around quick installation,
  visible output structure, preset selection, and provenance boundaries.
- Clarified that the package is a portable Agent Skill and replaced
  client-specific installation guidance with the Agent Skills CLI.

## [0.1.0] — 2026-08-06

- Added a Korean README and language switch links on both README pages.
- Published the complete standalone Agent Skill installation and workflow
  documentation.
- Validated the one-paper Reference workflow, note-quality checks, source-text
  provenance checks, and independent release layout.

## [0.1.0-beta.1] — 2026-08-06

- Added preset-first onboarding for notes-only, searchable-library, and
  knowledge-network use.
- Added the current Reference note schema with explicit record and promoted
  note types while preserving legacy Vault compatibility.
- Added local PDF extraction through Poppler and optional Docling, provenance
  manifests, hash verification, and an eight-case extraction corpus.
- Added standalone release smoke tests and one-paper workflow validation.
- Adopted the PolyForm Noncommercial License 1.0.0 for current releases.
- Added reproducible Agent Skill installation, update, and removal guidance.

[Unreleased]: https://github.com/moonweave/obsidian-reference-wiki/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/moonweave/obsidian-reference-wiki/releases/tag/v0.2.0
[0.1.0]: https://github.com/moonweave/obsidian-reference-wiki/releases/tag/v0.1.0
[0.1.0-beta.1]: https://github.com/moonweave/obsidian-reference-wiki/releases/tag/v0.1.0-beta.1
