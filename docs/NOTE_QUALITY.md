# Reference note quality contract

Reference note quality depends on the source text and the reading trace, not on
the amount of prose in a template. Keep the canonical source, the full parsed
text derivative, and the reviewed dossier distinct. The skill may use an LLM
to draft Markdown after the user supplies or authorizes the source, but it is
not an automatic library-wide ingestion or OCR pipeline. For one explicitly
approved PDF, `scripts/extract_source_text.py` provides the bounded
PDF-to-Markdown adapter described below.

## Source-text integrity

The full native-text/OCR file is a derived input for reading and retrieval. It
must not silently become the source of truth: native extraction can omit layout
and OCR can misread symbols. When supplied, create a `Source Text — …` manifest
with `source_text_storage`, location, `source_text_basis`, SHA-256 hash, and
page-map convention. Prefer `<!-- pdf-page: N -->` markers in Markdown
derivatives so a reviewed result can be traced back to the PDF page. The
manifest records provenance only; the Source dossier contains the
interpretation.

For an approved PDF with a usable text layer, run:

```bash
python scripts/extract_source_text.py <canonical.pdf> \
  --output <derived.md> --manifest <manifest.md> \
  --vault-root <approved-vault> --source-name <name> \
  --reference-type Paper --storage vault-local \
  --basis native-text --engine pdftotext
```

For a complex scientific PDF with formulas, columns, or nontrivial reading
order, prefer the local Docling path:

```bash
python scripts/extract_source_text.py <canonical.pdf> \
  --output <derived.md> --manifest <manifest.md> \
  --vault-root <approved-vault> --source-name <name> \
  --reference-type Paper --storage vault-local \
  --basis mixed --engine docling
```

The adapter records the canonical PDF hash and page count, extractor version,
options and mode, extracted-text page count, derivative hash, and one ordered
`pdf-page` marker for every canonical page. Docling runs locally with remote
services and external plugins disabled. Formula enrichment is intentionally
off by default because it can be substantially slower on CPU; add
`--docling-formula on` only when equation recovery justifies that cost. There
is no silent OCR: OCR is also off by default and requires
`--docling-ocr auto` for an authorized scan. There is no silent engine
fallback. Prefer `--docling-formula-pages 2,4-6` after identifying the exact
pages that need equation recovery. Each Docling pass defaults to a 600-second
timeout and leaves no final derivative or manifest on timeout. The adapter
refuses implicit overwrite and fails
on an engine or page-boundary error. Both outputs remain parsed derivatives:
visually check important equations, symbols, tables, captions, and multi-column
reading order before promoting claims.

`vault-local` is appropriate for a private Vault when full-text Obsidian or
agent search is part of the workflow. Render the derivative with
`templates/full-text.md`; do not add knowledge claims to that file. `external`
is safer for a shared or published Vault. The Blueprint must make the storage
choice and sharing consequence visible. The skill does not modify Git ignore,
sync, Publish, or `.obsidian` settings without separate approval.

When the derivative is absent, use `source_text_status: not supplied` and
`source_text_storage: not supplied`. That is an honest lower-evidence state and
does not justify creating a blank parse or inventing a summary.

## Obsidian title rendering

Obsidian displays the Markdown filename as an inline title when that setting is
enabled. Reference templates therefore do not repeat the filename as a top-
level `#` heading; content starts with semantic `##` sections. Do not turn off
or edit `.obsidian` to work around a duplicate title.

## Filename semantics

Use `Paper — {short title}` for an academic article and `Source — {name}` for
other external material. The prefix is part of the stable Markdown basename,
not a prose heading. Preserve an existing basename even when it predates this
default; link it through `reference_type` instead of renaming it silently.

## Handoff count gate

Run `python scripts/check_notes.py <approved-vault> --expect-sources
<approved-count> --expect-profile` before a preset-aware handoff. The approved
count includes both `Paper — …` and `Source — …` records. A count or profile
mismatch is a failed handoff; an exploratory run without the expectations is
not completion evidence.

## Two source states

- `not reviewed`: a capture note with only the canonical location, why it was
  queued, and the next reading action. It contains no paper summary or claim.
- `partial`: the source was read only in the named sections or excerpt. Every
  detail is labelled with its scope, and no broad claim is promoted.
- `reviewed`: the core paper map, method, theory/model, results, and limitations
  were checked, with a review trace and source anchors.

## Reading passes

For a supplied paper, use this order:

1. establish the text basis (`native-text`, `OCR`, `mixed`, or
   `supplied-excerpt`), record whether a full derived text artifact is
   available, and establish page/section numbering; use `unknown` only for an
   unread capture note;
2. map the problem, contribution, system, conditions, and paper structure;
3. read the method, measurement/analysis procedure, controls, and
   theory/model assumptions;
4. read results together with their figures/tables, preserving quantities,
   units, conditions, comparisons, and whether each result is measured,
   modelled, or calculated;
5. read the conclusion and stated limitations, then record any unread scope.

OCR is an input-recovery method, not a quality guarantee. Prefer a usable
native text layer; use OCR only when the text layer is missing or when a
figure/table requires it. Never copy the PDF or an OCR dump into the Vault by
default. Keep the exact external canonical location, derived-text manifest,
hash, page map, and compact review trace.

## Provenance rule

Each non-trivial result or promoted Claim must have an anchor such as `PDF p.
9 / printed p. 3147, §5, Fig. 11` and one of these labels: `reported`,
`modelled`, `calculated`, `author interpretation`, or `synthesis`. A numeric
value is incomplete without its unit, condition, comparison, and boundary.
When the paper does not supply a value or section, write `not supplied` or
`not reviewed`; do not fill the gap from a filename or general knowledge.

## Promotion gate

Promote a Claim, Method, Theory, Evidence, or Limitation only after the Source
dossier passes the relevant completeness checks. Promoted notes are concise
reusable indexes with source anchors, not copies of the dossier. If a source is
partial, keep its detail in the Source note and mark the unresolved scope.

## Executable handoff checks

The read-only checker is a structural gate, not a substitute for reading. In
addition to source count and dossier sections, it rejects unresolved template
placeholders, invalid text-basis values, duplicate Markdown basenames and
ambiguous wikilinks, top-level headings that mirror a filename, and reviewed
Evidence ledger bullets that lack both an evidence-type label and a page
anchor. A relation field may be `not provided`; the checker must not require a
Claim or Theme that the supplied record does not contain. When a derived text
manifest is available, verify its external file separately:

```bash
python scripts/check_source_text.py <source-text-manifest.md> --vault-root <approved-vault>
```

The checker treats missing, duplicate, or reordered page markers as failures
for provenance versions 1 and 2. Undecoded formula and image placeholders are
reported as quality warnings: the hash can be valid while scientific content
still needs visual review.

Run the deterministic parser corpus before release:

```bash
python scripts/run_extraction_corpus.py \
  --corpus evals/corpus/source-text-extraction/corpus.json \
  --engine pdftotext --json
```

The optional Docling run may return `quality_status: review-required` for a
known layout decision. That is a visible review queue, not permission to lower
the scientific reading gate.

Graph inspection is a presentation check, not a replacement for the Markdown
lint. Because `_templates` contains Markdown files, an unfiltered Obsidian
Graph can display template placeholders beside factual nodes. Exclude that
folder with the graph filter when the installed Obsidian version supports it;
otherwise review factual edges through Backlinks/Outgoing links. Do not edit
`.obsidian` automatically for this display preference.

## Source-to-dossier semantic regression

Run `scripts/score_dossier.py` against
`evals/corpus/reference-quality/corpus.json` for the fixed source-to-dossier
regression. It checks required fact coverage, expected evidence labels and PDF
anchors, quantitative value/unit/condition retention, and explicitly forbidden
contradictions. The good candidate must pass and the unsupported candidate
must fail. This small deterministic corpus catches known semantic regressions;
it does not replace human reading or a broader multi-paper benchmark.
