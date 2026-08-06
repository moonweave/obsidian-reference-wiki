# Obsidian Research Wiki: Reference

[한국어](README.ko.md) | English

> Turn papers into traceable knowledge—without losing the source.

`Obsidian Research Wiki: Reference` is a standalone Codex Skill for building a
provenance-first literature system in Obsidian. It keeps reviewed paper notes,
searchable source text, and reusable knowledge notes distinct, so a concise
summary never replaces the canonical PDF, web page, or Zotero item.

It works with a new or existing Vault and proposes a complete Blueprint before
creating files. Existing notes, `.obsidian` settings, plugins, PDFs, and Zotero
libraries remain untouched unless the user explicitly approves otherwise.

## Quick start

Git and Codex are the only requirements for notes-only use.

macOS or Linux:

```bash
mkdir -p "$HOME/.codex/skills"
git clone https://github.com/moonweave/obsidian-reference-wiki.git \
  "$HOME/.codex/skills/obsidian-research-wiki-reference"
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME/.codex/skills" | Out-Null
git clone https://github.com/moonweave/obsidian-reference-wiki.git `
  "$HOME/.codex/skills/obsidian-research-wiki-reference"
```

Start a new Codex session, then run:

```text
$obsidian-research-wiki-reference Design a literature Vault.
```

> [!NOTE]
> The first response is a design conversation. No Vault file is created until
> the exact path, Blueprint, pilot sources, and no-touch list are approved.

See the [installation guide](docs/INSTALLATION.md) for verification, updates,
safe disabling, Windows notes, and optional PDF dependencies.

## What you get

A first pilot creates a navigable route from the Reference Index to a real
paper or source. Additional knowledge notes are created only when they are
useful beyond one paper.

```text
Reference Index
├── Reference Profile
├── Paper — Short title
│   ├── reviewed method, results, limitations, and source anchors
│   └── Source Text Manifest — Short title  (optional)
├── Claim — Reusable finding               (optional)
├── Method — Reusable literature method    (optional)
└── Theory — Source-grounded model          (optional)
```

Paper dossiers remain the primary reading record. Claim, Method, Theory,
Evidence, Limitation, Theme, and Question notes are selective promotion
targets—not fragments created for every paragraph.

Academic articles use `Paper — {short title}`. Reports, web pages, standards,
datasets, and other external material use `Source — {name}`. Existing
basenames and links are preserved. Name collisions are resolved predictably by
adding the year and then the first author.

## Choose the depth

The first onboarding choice controls how far the literature is organized.
`searchable-library` is recommended for most users.

| Preset | Includes | Best for |
| --- | --- | --- |
| `notes-only` | Paper/Source dossiers | Focused reading |
| `searchable-library` | Dossiers + searchable text | Most libraries |
| `knowledge-network` | Above + promoted notes | Cross-paper synthesis |

The presets are cumulative, but full-text storage is a separate safety
decision. A private Vault can use a regenerable `vault-local` cache. Shared,
published, publicly synchronized, or uncertain Vaults are directed to
`external` storage. The approved choices are persisted in a `Reference
Profile`.

## Four representations, four jobs

1. **Canonical source** — the authoritative PDF, web page, or Zotero item,
   normally outside the Vault.
2. **Derived source text** — optional native-text/OCR Markdown for search and
   rereading; useful, but vulnerable to parsing and OCR errors.
3. **Paper or Source dossier** — the reviewed meaning of one source, including
   method, measurements, model assumptions, results, limitations, and trace.
4. **Promoted knowledge note** — a concise Claim, Method, Theory, Evidence,
   Limitation, Theme, or Question reused across sources.

The derived text is never treated as raw truth. Important equations, symbols,
tables, figures, captions, and multi-column reading order still require visual
comparison with the canonical source.

## Optional local PDF extraction

For an explicitly approved PDF, the bundled adapter keeps the canonical file
external and creates a page-marked derivative plus a provenance manifest.

- `pdftotext` provides the compatible path for PDFs with a usable text layer.
- Docling is available for complex scientific layouts; OCR and formula
  enrichment remain explicit options.
- New manifests record canonical and derivative hashes, extractor metadata,
  options, page counts, and ordered page markers.
- Existing outputs are never overwritten implicitly, and there is no silent
  fallback between extraction engines.

Commands and dependency setup are documented in
[docs/INSTALLATION.md](docs/INSTALLATION.md). The full extraction and review
contract is in [docs/NOTE_QUALITY.md](docs/NOTE_QUALITY.md).

## Safety boundaries

- Design mode is read-only.
- Apply requires an exact Vault path and an approved Blueprint.
- Existing notes are linked in place by default, not moved or renamed.
- The Skill does not install Obsidian plugins or modify `.obsidian` settings.
- It does not copy PDFs, Zotero libraries, original research data, or code.
- It does not create experiment, observation, or laboratory-record structures.
- It does not infer paper content from filenames.

## Quality checks

Before handing off a real Vault, run the read-only note check with the exact
source count approved in the Blueprint:

```bash
REFERENCE_SCHEMA_MODE=current python scripts/check_notes.py <approved-vault> \
  --expect-sources <approved-count> \
  --expect-profile
```

If derived source text is present, verify its hash and page map separately:

```bash
python scripts/check_source_text.py <manifest.md> --vault-root <approved-vault>
```

Repository maintainers can run the standalone release smoke with:

```bash
python scripts/smoke_release.py
```

These checks catch structural and provenance errors. They do not replace
reading the source or reviewing scientific claims.

## Documentation

- [Operating contract](SKILL.md)
- [Reference architecture](docs/CONTRACT.md)
- [Onboarding interview](docs/ONBOARDING.md)
- [Installation and PDF extraction](docs/INSTALLATION.md)
- [Note-quality contract](docs/NOTE_QUALITY.md)
- [Workflow usability protocol](docs/USABILITY_TEST.md)
- [Release history](CHANGELOG.md)
- [Security policy](SECURITY.md)
- [Feedback and contributions](CONTRIBUTING.md)

All templates, evaluation cases, and verification scripts are bundled in this
repository, so the Skill can be installed and evaluated without a sibling
repository.

## License

Current releases use the
[PolyForm Noncommercial License 1.0.0](LICENSE). Personal research, study,
experimentation, educational-institution use, and public-research-organization
use are permitted under its terms. Commercial use requires a separate license
from Moonweave. This repository is source-available, not OSI-approved open
source.

The license change is prospective. Versions released at or before commit
`8a43fd2` remain under the MIT License that applied to those versions.
