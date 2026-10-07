# Obsidian Research Wiki: Reference

[한국어](README.ko.md) | English

> Turn papers into traceable knowledge—without losing the source.

`Obsidian Research Wiki: Reference` is a standalone Agent Skill for building a
provenance-first literature system in Obsidian. It follows the open
[Agent Skills specification](https://agentskills.io/specification) and keeps
reviewed paper notes, searchable source text, and reusable knowledge notes
distinct, so a concise summary never replaces the canonical PDF, web page, or
Zotero item.

It works with a new or existing Vault and proposes a complete Blueprint before
creating files. Existing notes, `.obsidian` settings, plugins, PDFs, and Zotero
libraries remain untouched unless the user explicitly approves otherwise.

## Quick start

If you would rather follow screenshots and plain steps than a command, read the
[install and usage guide](https://moonweave.github.io/obsidian-reference-wiki/guide.html).
It covers Claude Code and Codex, and gets you there without a terminal.

Otherwise, install it with the skill manager supported by your agent. With the
portable Skills CLI:

```bash
npx skills add moonweave/obsidian-reference-wiki
```

The installer detects compatible agents and lets you choose the target and
installation scope. Start a new agent session, then ask:

```text
Use obsidian-research-wiki-reference to design a literature Vault.
```

> [!NOTE]
> The first response is a design conversation. No Vault file is created until
> the exact path, Blueprint, pilot sources, and no-touch list are approved.

See the [installation guide](docs/INSTALLATION.md) for package inspection,
manual installation, updates, removal, and optional PDF dependencies.

## Asking the Vault

Once notes exist, the same skill answers from them. Ask where a value came
from, what a stored paper reported, or which notes support a claim, and the
answer arrives with the page anchor the note recorded:

```text
"이 수치 어디서 나왔어?"
→ 440 V 직류에서 1 kg 이상 [reported]
   Provenance anchor: PDF p. 1 / printed p. 713, Fig. 1
   Paper — Electro-adhesion and its applications
```

Answering is read-only. It never invents a value the notes do not hold, never
promotes a modelled number into a measurement, and never edits the Vault as a
side effect of a question.

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

<!-- progress:start -->
## Field results

Does an AI answering from a library organised with this skill make things up? Measured on the maintainer's own library of 565 papers. Updated 2026-10-07.

**3%** of AI claims had no support in the cited paper · **40/40** unanswerable questions declined · **96%** of answerable questions answered with a correct source

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/progress/figure-dark.svg">
  <img alt="Headline numbers (hallucination rate, refusals, answer accuracy) and a chart of how the library improved" src="docs/progress/figure-light.svg" width="100%">
</picture>

One person's library and question set, with an AI judge checked against planted errors and every flagged line re-checked by a stronger model; the numbers are not comparable to public leaderboards. The judge catches reversed meanings, and a separate rule flags "first", "best" or "only" wording the source does not support; subtler distortions can still slip through, so the hallucination rate may be an underestimate. Searching and answering use the maintainer's own search tools, which are not part of this skill; the skill contributes the review labels and PDF page numbers that let answers be checked.

<details>
<summary>All metrics</summary>

| Metric | First (2026-10-06) | Latest (2026-10-07) |
|---|---|---|
| AI answer score (CRAG) | 0.947 | 0.947 |
| AI answers with a correct source | 96% | 96% |
| AI declines unanswerable questions | 100% | 100% |
| AI claims backed by the cited paper | 93% | 97% |
| AI citations that back a claim | 93% | 97% |
| Cited PDF page holds the claim | 93% | 98% |
| Right paper ranked first: Exact wording | 0.625 | 0.833 |
| Right paper ranked first: Paraphrased | 0.667 | 0.750 |
| Right paper ranked first: Multi-paper | 0.929 | 0.857 |
| Right paper ranked first: Provenance | 0.733 | 0.867 |
| Right paper ranked first: Korean questions | 0.358 | 0.358 |
| Search engine alone: answer score (English) | 0.546 | 0.546 |
| Search engine alone: answer score (Korean) | -0.151 | -0.151 |
| Search engine alone: declines unanswerable | 0% | 0% |
| Papers labelled with review depth | 2% | 100% |
| Summaries marked abstract-based | 1% | 100% |
| Facts with a PDF page | 0% | 46% |
| Gold evidence traceable to a page | 65% | 65% |
| Fully reviewed papers (page-anchored dossiers) | 0 | 0 |

Grounded-answer score follows [CRAG](https://github.com/facebookresearch/CRAG): a right answer scores +1, declining scores 0, and a wrong or unsupported answer scores −1. Claim support follows the faithfulness / groundedness measures of RAGAS and TruLens; citation support follows [ALCE](https://github.com/princeton-nlp/ALCE). "First" is the earliest recorded value of each metric.

</details>
<!-- progress:end -->

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
