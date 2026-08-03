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
evals/evals.json
templates/
  claim.md
  evidence-method.md
  method.md
  limitation.md
  question.md
  reading-queue.md
  reference-index.md
  source.md
  theme.md
  theory-background.md
```

The templates are deliberately product-local so this repository can be
installed and evaluated without a sibling repository or a shared skill.

## Evaluation

The product evaluation cases are stored in [evals/evals.json](evals/evals.json).
They cover a new reference Vault, an existing mixed Vault, provenance-safe
source capture, and the boundary between reference organization and research
records.

## License

MIT. See [LICENSE](LICENSE).
