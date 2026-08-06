# Obsidian Research Wiki: Reference

[한국어](README.ko.md) | English

`Obsidian Research Wiki: Reference` is a source-available, provenance-first skill
for organizing literature in Obsidian. It gives papers, sources, claims,
evidence, methods, theories, limitations, themes, and literature questions a coherent
structure without turning the Vault into a research-log or experiment system.
It also gives literature methods and source-grounded background theories their
own notes, distinct from the user's research protocol.

Paper notes remain the primary reading record. Standalone Claim, Method,
Theory, Evidence, or Limitation notes are optional promotion targets for
cross-paper reuse, active questions, independent revision, or distinct
provenance.

Academic articles default to `Paper — {short title}`. Reports, web pages,
standards, datasets, and other external material use `Source — {name}`. Existing
`Source — …` paper notes remain valid and are never renamed automatically.
When a basename collides, the stable suffix order is year, then first author.

The note-quality workflow in `docs/NOTE_QUALITY.md` keeps text basis, review
scope, method, measurements, model assumptions, anchored results, and
limitations visible instead of compressing a paper into an unsupported
paragraph.

On first run, the skill first offers notes only, searchable library
(recommended), or knowledge network. That depth preset maps to `paper-first`,
`balanced`, or `concept-network`, while source-text storage remains an
independent safety choice. The approved choice is persisted in a validated
`Reference Profile`, including source-text policy, availability, storage, and
readiness. Private Vaults that need agent/Obsidian full-text
search can use a vault-local regenerable cache; shared, published, publicly
synchronized, or uncertain Vaults are steered to external storage.

For an explicitly approved pilot PDF, `scripts/extract_source_text.py` keeps
the canonical PDF external and provides two local adapters: the compatible
`pdftotext` path and a Docling path for complex scientific layout. Docling OCR
and formula enrichment are separate explicit options. Every new derivative
records provenance version 2, engine options, hashes, and ordered page markers;
`scripts/check_source_text.py` also reports undecoded formulas and images with
per-page counts for targeted recovery and visual review.
High-cost Docling work defaults to a 600-second limit per pass, and reviewed
formula pages can be selected without enriching the full document.

## What it does

- designs or safely onboards a reference-focused Obsidian Vault;
- diagnoses retrieval style and recommends an architecture with reasons before
  asking for Apply approval;
- preserves source provenance and records canonical Zotero or external links;
- connects sources to claims, evidence methods, literature methods,
  background theories, limitations, themes, and questions with real Obsidian
  wikilinks;
- supports an existing Vault through read-only inspection first and staged,
  explicitly approved changes.

## What it does not do

- copy PDFs, Zotero libraries, original data, code, or external source files;
- install plugins or modify `.obsidian` settings by default;
- create experiment, observation, or laboratory-record structures;
- infer research facts from filenames or perform bulk migration;
- replace the separate `research-wiki` retrieval and query skill.

## Safety boundary

Design mode does not install, create, move, delete, or modify Vault files. Apply
mode requires the exact Vault path and an approved Blueprint. Existing notes
remain in place unless a separate move approval is given; linking from a new
note is the default migration path.

## Install

The technical skill identifier is `obsidian-research-wiki-reference`. Install
the repository directly into the Codex skill directory.

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

Start a new Codex session, then try:

```text
$obsidian-research-wiki-reference Help me design a literature Vault. Do not create files yet.
```

The full [installation guide](docs/INSTALLATION.md) includes verification,
updating, safe disabling, Windows notes, and optional PDF dependencies. The
operating contract is in [SKILL.md](SKILL.md), and the reference architecture
is in [docs/CONTRACT.md](docs/CONTRACT.md).

## Included layout

```text
README.md
README.ko.md
SKILL.md
CHANGELOG.md
CONTRIBUTING.md
LICENSE
NOTICE
SECURITY.md
docs/CONTRACT.md
docs/USABILITY_TEST.md
docs/INSTALLATION.md
docs/NOTE_QUALITY.md
docs/ONBOARDING.md
evals/evals.json
scripts/check_notes.py
scripts/check_source_text.py
scripts/extract_source_text.py
scripts/recommend_profile.py
scripts/run_extraction_corpus.py
scripts/smoke_release.py
templates/
  claim.md
  evidence.md
  full-text.md
  method.md
  limitation.md
  question.md
  reading-queue.md
  reference-index.md
  reference-profile.md
  source-capture.md
  source.md
  source-text-manifest.md
  theme.md
  theory.md
```

The templates are deliberately product-local so this repository can be
installed and evaluated without a sibling repository or a shared skill.

## Evaluation

The product evaluation cases are stored in [evals/evals.json](evals/evals.json).
They cover a new reference Blueprint, an existing mixed Vault, the boundary
between reference organization and research records, and private-full-text
versus shared-Vault onboarding. Capture and reviewed-note quality are
additionally exercised through the product templates,
`scripts/recommend_profile.py`, `scripts/check_notes.py`, and
`scripts/check_source_text.py`. Source-text verification requires the exact
approved `--vault-root` and rejects relative-path and symlink escapes.

The read-only lint is a quality check over discovered notes, not proof that the
correct Vault was selected. Handoff runs it with the approved Blueprint count:

```bash
REFERENCE_SCHEMA_MODE=current python scripts/check_notes.py <approved-vault> \
  --expect-sources <approved-count> \
  --expect-profile
```

A count or profile mismatch fails. A run without these expectations is
exploratory only. The smoke verifies the source contract and synthetic Apply;
it does not prove the wording of an actual agent's first response.

Run the standalone release smoke before publishing or installing a local copy:

```bash
python scripts/smoke_release.py
```

It uses a temporary synthetic Vault to verify the first Reference route,
reviewed and unread source states, onboarding profile recommendations, a
vault-local derived-text cache and manifest, hash verification, wikilink
resolution, expected source count, and the absence of experiment/observation
records. The synthetic full text is temporary and is not bundled into this
public repository.

The repository-owned eight-case extraction corpus is a separate parser gate:

```bash
python scripts/run_extraction_corpus.py \
  --corpus evals/corpus/source-text-extraction/corpus.json \
  --engine pdftotext --json
```

Docling results may deliberately report `quality_status: review-required`;
automated structure checks never substitute for equation, figure, or scientific
review.

## Project policies

- Release history: [CHANGELOG.md](CHANGELOG.md)
- Security reports: [SECURITY.md](SECURITY.md)
- Feedback and contributions: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

The current release is licensed under the
[PolyForm Noncommercial License 1.0.0](LICENSE), SPDX identifier
`PolyForm-Noncommercial-1.0.0`.

Personal research, study, experimentation, educational-institution use, and
public-research-organization use are permitted under its terms. Commercial use
requires a separate license from Moonweave. This is a source-available license,
not an OSI-approved open-source license.

The license change is prospective. Versions released at or before commit
`8a43fd2` remain available under the MIT License that applied to those versions.
