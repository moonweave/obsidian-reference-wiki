---
name: obsidian-research-wiki-reference
description: Design, safely onboard, or extend an Obsidian reference knowledge system for papers, Zotero, citations, claims, evidence, literature methods, background theories, limitations, themes, and literature questions. Use for rigorous literature/reference organization, not research records or combined workspaces.
---

# Obsidian Research Wiki: Reference

Onboard into a complete external-knowledge architecture, never a shallow starter. Design mode reads only user-authorized paths. Apply requires exact Vault path and Blueprint approval; it never changes `.obsidian`, installs plugins, copies PDFs/Zotero files, or moves existing notes. A full parsed/OCR text file is a derived reading input, not a replacement for the canonical source or a knowledge note.

Read [the local contract](docs/CONTRACT.md) and
[the onboarding interview](docs/ONBOARDING.md) before acting. Explain the plan
in the user's language and keep Design and Apply visibly separate.

## Installation and Vault location

If Obsidian is not installed on macOS, direct the user to the official
Obsidian download page and explain that the user installs and opens the app;
the skill does not install software. Then guide `Create new vault`, propose a
location outside Zotero storage, ask the user to confirm the exact path, and
stop before creating it. A Vault is the Markdown workspace, not a copy of the
PDF library. Do not create a second Vault if the user has an authorized one.

## Entry gate

Every request that would create or change a Vault file passes through this
gate, whatever the user opened with. A dropped PDF, `이 논문 정리해줘`, a Zotero
folder, or an explicit onboarding request all arrive at the same check. Do not
treat a task-shaped opening as permission to skip it.

1. Resolve the target Vault, then look for a `Reference Profile` in it.
2. Profile found: read it, follow it, and do not ask again. State the mode you
   are applying in one line so the user can correct it, then continue with the
   request.
3. No profile: run the first-run interview below before any file is created.

The profile is the record of what the user agreed to, so onboarding happens
once per Vault rather than once per conversation. A user who has answered
already must never be asked a second time.

## First-run workflow

Ask what the user can answer now, and defer what depends on having notes. Reuse
facts they already supplied and do not re-ask them.

1. Ask one plain-language question that shows all three peer presets up front:
   `notes-only`, `searchable-library`, and `knowledge-network`. Explain them as
   reviewed Paper/Source dossiers; dossiers plus searchable full text; or both
   plus selectively promoted cross-paper knowledge. Recommend
   `searchable-library` when the user is unsure, and explain that the presets
   are cumulative capabilities rather than incompatible schemas. Never hide or
   defer `knowledge-network` merely to simplify the first choice.
2. Ask the safety facts only when the answer changes what you write. Extraction
   needs to know whether the Vault is private or shared and how far it
   synchronizes; notes only does not. Map the answer with
   `scripts/recommend_profile.py --preset ...` so the same inputs produce the
   same profile. `notes-only` maps to `paper-first`; `searchable-library` to
   `balanced`; and `knowledge-network` maps to `concept-network`.
   Preserve the legacy retrieval/full-text arguments for existing callers.
3. Confirm the execution facts: new or existing exact Vault path; first Apply
   scope (default pilot: one to three supplied sources); and the exact
   preservation/no-touch list.
4. Inspect an existing Vault only after the user names it. Report the baseline
   without treating file names as facts.
5. Return a Blueprint with the selected mode, mapped configuration and
   rationale, a persisted `Reference Profile`, complete map, note meanings,
   placement rules, labelled link rules,
   canonical-source boundary, source-text mode, first real source route,
   approved mutation set, and no-touch list.
6. Wait for approval of the exact path, Blueprint, and supplied source facts.
7. Apply only the approved folders, templates, persisted profile, and factual
   notes. Create an unread source as a capture note only when the user supplied
   its location; mark its content `not reviewed`.

## Required first path

The approved first path must be resolvable from `Reference Index` to a real
Paper or Source and then to a Claim, or explicitly stop at that reference when no claim was
supplied. Evidence, Method, Theory, and Limitation links are created only when
supplied. The default domains are `10 Sources`, `20 Claims`, `30 Evidence &
Methods`, `35 Theories`, `40 Limitations`, `50 Themes`, `60
Questions`, `90 Reading Queue`, and `_templates`; do not add research-record
domains.

Relation fields are selective: render `Claim: not provided`, `Claim affected:
not provided`, or `Theme: not provided` when the user did not supply that node.
Never manufacture a wikilink merely to make the graph look complete.

Use `Paper — {short title}` for academic articles and `Source — {name}` for
reports, web pages, standards, datasets, or other external material. Preserve
existing `Source — …` paper basenames and links; do not rename them as part of
onboarding. Set `reference_type` to the actual prefix when rendering links.
Start with the short title; on a basename collision append `— {year}`, then
append `— {first author}` only if the title and year still collide.

## Source-text layer

Keep four representations distinct:

1. the canonical PDF, web page, or Zotero item outside the Vault;
2. an optional full native-text/OCR Markdown or text derivative used as the
   LLM reading input;
3. the `Paper — …` or `Source — …` dossier that records the reviewed meaning;
4. promoted Claim, Method, Theory, Evidence, Limitation, or Theme notes.

Serialize an external local file recorded in a frontmatter location field as
a percent-encoded `file:///` URI, for example by using Python
`Path.resolve().as_uri()`. This prevents an `@` inside a cloud-storage folder
name from being misread by Obsidian as an email link. Because Markdown is not
rendered inside Properties, also render an explicit `Open canonical source`
Markdown link in the dossier body. Continue accepting legacy absolute paths
when reading existing notes; migrate only notes in the approved mutation set.
Vault-local derivative locations remain relative paths.

The derived text is not raw truth: OCR can introduce errors and parsing can
lose layout. Recommend `vault-local` when a private researcher wants Obsidian
or an agent to search and reread the full text. Render the cache with
`templates/full-text.md` under the exact approved `05 Source Text/Full Text`
path. Recommend `external` when the Vault is shared, published, or subject to
copyright/synchronization risk. A vault-local cache is a regenerable derivative,
not permission to copy the PDF, and it must not silently enter Git, Publish, or
another sharing surface.

For either storage mode, keep the derivative unchanged after extraction and
record `source_text_storage`, exact location, extraction basis, SHA-256 hash,
and page-marker convention in `Source Text Manifest — …` using
`templates/source-text-manifest.md`. Create that manifest only when the
derivative is supplied or explicitly authorized. If it is unavailable, write
`not supplied`; do not create an empty text file or summarize from its
filename. The manifest is provenance metadata, not a second knowledge dossier.

Use the standard marker `<!-- pdf-page: N -->` in a Markdown derivative when
page-level anchors are preserved. Run `python scripts/check_source_text.py
<manifest.md> --vault-root <approved-vault>` only after the exact Vault,
manifest, and derivative path are approved;
it reads the named derivative, verifies its hash, and checks the declared page
markers without modifying either file. A changed hash marks the dossier for
review; it does not authorize automatic rewriting of claims.

When the user explicitly authorizes extracting one PDF, use
`python scripts/extract_source_text.py <canonical.pdf> --output <derived.md>
--manifest <manifest.md> --vault-root <approved-vault> --source-name <name>
--reference-type <Paper|Source> --storage <vault-local|external> --basis
native-text --engine pdftotext` for the compatibility path. For a complex
scientific PDF where formulas, columns, or reading order matter, prefer
`--basis mixed --engine docling`. Docling runs locally with remote services and
external plugins disabled and no silent fallback to `pdftotext`. Formula
enrichment is an explicit high-cost option, `--docling-formula on`; leave it
off for the first layout pass. Prefer `--docling-formula-pages 2,4-6` when only
reviewed pages need equation recovery. Every Docling pass has a default
600-second limit, adjustable with `--docling-timeout-seconds`; timeout failure
writes neither final artifact. The adapter keeps the canonical PDF external,
creates ordered page markers, records canonical and derivative hashes plus extractor metadata,
and refuses existing outputs unless `--overwrite` is explicitly supplied. If
the selected engine fails or cannot preserve every page boundary, stop at an
extraction failure. Treat either derivative as parsed input that still needs
formula and reading-order review, not as source truth.

Before describing a release as parser-tested, run the repository-owned
eight-case layout corpus with `scripts/run_extraction_corpus.py`. A green
structural corpus does not accept equations, figures, or scientific claims.
Use `docs/USABILITY_TEST.md` when evaluating the workflow with another
researcher.

## Method and theory boundary

`Method` in Reference means a method described or used by a paper: its purpose,
source-reported procedure, assumptions, and stated boundary. It is not the
user's own experimental protocol; Research owns that record. `Theory` means a
source-grounded background mechanism, model, or conceptual framework that is
reused across claims. Do not turn a paper's background discussion into a
scientific fact beyond what the supplied source supports.

## Reference-record capture and selective promotion

Create one Source note per paper as the reading record. Keep the paper-specific
abstract or scope, method as used by that paper, background theory, reported
evidence or results, and supplied limitations together in that Source note.

Promote a Claim, Method, Theory, Evidence, or Limitation to its own note only
when it is reused across sources, answers an active literature question, needs
independent links or revision, or has a distinct provenance boundary. A
promoted note is a concise reusable index with a link back to the Source; it is
not a second copy of the paper's full discussion. If none of those conditions
hold, keep the detail in the Source note.

## Reading and note-quality workflow

The LLM may draft and populate Markdown only after the user supplies or
authorizes the source or derived text. This skill is not an automatic
PDF-ingestion or OCR pipeline. Use `source-capture.md` for an unread source; it
records only the canonical location, capture reason, and next action. When a
derived text artifact exists, read it together with the source's page/section
map, then write the dossier; never treat the full parse itself as a reviewed
claim.

For a reviewed source, record the text basis (`native-text`, `OCR`, `mixed`, or
`supplied-excerpt`) and read in passes: paper map; method, measurements,
controls, and theory/model; results with figures/tables; then conclusion and
limitations. Preserve page/section/figure anchors, units, conditions, and
comparisons. Label each important item as `reported`, `modelled`, `calculated`,
`author interpretation`, or `synthesis`. Use `not supplied` or `not reviewed`
when the paper does not support a detail. Do not promote a node until the
Source dossier has a review trace and the relevant provenance fields.

Before handoff, run the product-local read-only lint with `REFERENCE_SCHEMA_MODE=current python
scripts/check_notes.py <approved-vault> --expect-sources <approved-count>
--expect-profile`.
It checks Paper/Source count, source-text status and manifest metadata,
text-basis enum, substantive required dossier sections, per-result
evidence-ledger anchors and labels, promoted-note provenance and reviewed-source
status, unresolved placeholders, duplicate
basenames, filename-mirroring headings, and resolving wikilinks; it never
edits the Vault. Run `check_source_text.py` separately with the approved
`--vault-root` when the approved derived artifact itself must be hash-verified.
The expected count comes from the approved Blueprint. A bare lint run without
`--expect-sources` is exploratory only and is not handoff evidence.

When visually reviewing an Obsidian Graph, exclude `_templates` with the
version's graph filter when available (for example, `-path:_templates`). If
that UI does not expose a filter, use Backlinks/Outgoing links or the file list
for the factual review. Template Markdown can otherwise appear as
`{claim_name}`-style graph nodes; those are not research records, and the skill
does not edit `.obsidian` automatically to hide them.

## Existing Vault and handoff

For a mixed Vault, the baseline ledger must use exactly `keep in place`, `link
from a new note`, or `move later only with separate approval`. Do not perform a
bulk migration under a first-link approval. Before handoff, resolve every
outgoing link, confirm canonical locations remain external, report unreviewed
material, and list `.obsidian`, existing notes, source files, and plugins that
were untouched.

Propose `Reference Index`, `Reference Profile`, `Sources` or an equivalent existing `Papers` domain, `Claims`, `Evidence & Methods`, `Theories`, `Limitations`, `Themes`, `Questions`, `Reading Queue`, and `_templates`. A first route uses real links: `[[Reference Index]] -> [[Reference Profile]]` and `[[Reference Index]] -> [[Paper — …]]` for an academic article or `[[Source — …]]` for other material, then adds a Claim or promoted node only when the reference supports it. Create factual records only from supplied content or explicitly authorized reading; record canonical locations, never copies. Existing Vaults receive a read-only `keep in place` / `link from a new note` / `move later only with separate approval` ledger. Verify every wikilink resolves and report provenance, next action, and untouched material.
