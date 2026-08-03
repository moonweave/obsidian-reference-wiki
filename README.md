# Obsidian Research Wiki: Reference

`Obsidian Research Wiki: Reference` is a standalone, provenance-first skill
for organizing literature in Obsidian. It gives papers, sources, claims,
evidence methods, limitations, themes, and literature questions a coherent
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

The note-quality workflow in `docs/NOTE_QUALITY.md` keeps text basis, review
scope, method, measurements, model assumptions, anchored results, and
limitations visible instead of compressing a paper into an unsupported
paragraph.

## What it does

- designs or safely onboards a reference-focused Obsidian Vault;
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

The technical skill identifier is `obsidian-research-wiki-reference`. For a
Codex installation, make this repository available at:

```text
~/.codex/skills/obsidian-research-wiki-reference
```

Then invoke the skill when the task is about rigorous literature or reference
organization. The full operating contract is in [SKILL.md](SKILL.md), and the
reference architecture is in [docs/CONTRACT.md](docs/CONTRACT.md).

## Included layout

```text
SKILL.md
docs/CONTRACT.md
docs/NOTE_QUALITY.md
evals/evals.json
scripts/check_notes.py
scripts/check_source_text.py
scripts/smoke_release.py
templates/
  claim.md
  evidence-method.md
  method.md
  limitation.md
  question.md
  reading-queue.md
  reference-index.md
  source-capture.md
  source.md
  source-text-manifest.md
  theme.md
  theory-background.md
```

The templates are deliberately product-local so this repository can be
installed and evaluated without a sibling repository or a shared skill.

## Evaluation

The product evaluation cases are stored in [evals/evals.json](evals/evals.json).
They cover a new reference Blueprint, an existing mixed Vault, and the boundary
between reference organization and research records. Capture and reviewed-note
quality are additionally exercised through the product templates and
`scripts/check_notes.py` and `scripts/check_source_text.py`.

The read-only lint is a quality check over discovered notes, not proof that the
correct Vault was selected. Handoff runs it with the approved Blueprint count:

```bash
python scripts/check_notes.py <approved-vault> --expect-sources <approved-count>
```

A count mismatch fails. A run without `--expect-sources` is exploratory only.

Run the standalone release smoke before publishing or installing a local copy:

```bash
python scripts/smoke_release.py
```

It uses a temporary synthetic Vault to verify the first Reference route,
reviewed and unread source states, a derived source-text manifest and hash,
wikilink resolution, expected source count, and the absence of
experiment/observation records. The full parsed text remains a temporary
external derivative; it is not bundled into this public repository.

## License

MIT. See [LICENSE](LICENSE).
