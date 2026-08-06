# Reference contract

`contract_version: 12`

Reference owns external knowledge: source provenance, claims, evidence,
literature methods, background theories, limitations, themes, questions, and
reading queue. It does not own the user's experiment history, raw data, code,
or next research decision.

Design mode is read-only and limited to paths the user names. Apply requires
an exact Vault path and an approved Blueprint. The default mutation set is
folders, approved templates, and supplied factual notes. `.obsidian`, plugins,
bulk moves, renames, deletes, and copies of source material remain out of
scope.

First run uses the two-stage interview in `docs/ONBOARDING.md`. Stage 1 starts
with one depth preset: `notes-only`, `searchable-library` (the default), or
`knowledge-network`. It then checks the sharing boundary, synchronization
exposure, and current source workflow before mapping the preset to an
organization mode and a safe source-text storage mode. Stage 2 confirms the
exact Vault path, a bounded first Apply scope, and the no-touch list. The skill
recommends a configuration; it does not make the user design the taxonomy from
scratch.

The preset is an onboarding layer over the existing note schema. Persist the
approved choice in exactly one `Reference Profile` linked from `Reference
Index`; do not rely on chat history. `notes-only` maps to `paper-first` and
does not create or import a full-text derivative;
`searchable-library` maps to `balanced` and requests searchable full text;
`knowledge-network` maps to `concept-network` and lowers the selective
promotion threshold. Existing derivatives and notes are preserved when a
shallower preset is chosen. Shared/published use or public/uncertain
synchronization forces `external` only when `source_text_policy: searchable`
and an authorized derivative is available.

The profile separates intent from artifact state. It records `preset`,
`organization_mode`, `source_text_policy`, `source_text_availability`,
`source_text_storage`, `preset_status`, `sharing`, and `sync_exposure`.
`notes-only` is `omit + not-applicable + ready`, even when an existing
derivative is known and preserved externally. A searchable preset without an
authorized derivative is `unavailable + not supplied + pending-source-text`;
it must not be described as search-ready.

Every factual note must say what was supplied and preserve its canonical
location. Unread material is labelled `not reviewed`; it is never summarized
from a filename. Existing Vault candidates are classified as `keep in place`,
`link from a new note`, or `move later only with separate approval`.

Reference `Method` notes describe a method as reported by a source. Research
`Method` notes describe the user's own research process; the two meanings must
not be merged. `Theory` notes capture source-grounded background mechanisms,
models, or conceptual frameworks and must retain their source link plus a
claim link when a claim was supplied. Optional claim/theme relations are
written explicitly as `not provided`; a graph edge is never invented.

The Source note is the paper-first reading record. It may contain the paper's
abstract or scope, method, theory, evidence, and limitations together. Standalone
Claim, Method, Theory, Evidence, or Limitation notes are promoted only when
they are reusable, question-relevant, independently revised, or provenance-
distinct; promotion must not duplicate the full Source note.

Academic articles use the filename `Paper — {short title}` by default. Reports,
web pages, standards, datasets, and other external materials use `Source —
{name}`. Both are reference records and may live in a `Sources` or `Papers`
navigation folder. Existing `Source — …` paper notes remain valid and are
linked in place; adopting `Paper — …` never authorizes an automatic rename.
Templates use `reference_type` so every wikilink targets the actual basename.

The source has a separate derived-text boundary. The canonical PDF, web page,
or Zotero item remains external and authoritative. A supplied native-text/OCR
Markdown or text derivative is an immutable reading input. For a private Vault
that benefits from full-text agent or Obsidian search, `vault-local` may place
the derivative under the exact approved `05 Source Text/Full Text` path. For a
shared, published, publicly synchronized, or uncertain Vault, recommend
`external`. `Source Text — …` is a
manifest for either mode; it records `source_text_storage`,
`source_text_location`, `source_text_basis`, `source_text_hash`, and
`source_text_page_map`, but it is not a summary or a Claim. A vault-local file
is a regenerable cache, not a copied PDF or an authoritative knowledge note.
If no derivative was supplied, record `source_text_status: not supplied` and
`source_text_storage: not supplied`; create no empty placeholder file.
Artifact verification requires the exact approved `--vault-root`; reject a
vault-local path whose resolved target, including symlinks, is outside it.

When the user authorizes PDF text extraction,
`scripts/extract_source_text.py` creates the page-marked derivative and its
manifest from explicit input/output paths. `--engine pdftotext --basis
native-text` remains the compatibility path. `--engine docling --basis mixed`
is the recommended local path for complex scientific PDFs. It disables remote
services and external plugins. Formula enrichment is disabled by default and
requires the explicit high-cost `--docling-formula on` option. Selective
recovery uses `--docling-formula-pages` with one layout pass and one enriched
page-range pass. Each pass defaults to a 600-second timeout. Neither path falls
back silently. The adapter never overwrites without `--overwrite` and
rejects a canonical PDF inside the Vault. Existing provenance version 1
manifests remain valid. New provenance version 2 records the canonical PDF
hash/page count, extractor/version/options/mode, extracted-text page count,
derivative hash, and a complete ordered marker for every PDF page. Any engine
failure or page-boundary mismatch is an explicit failure.

The public extraction corpus contains eight generated layout cases and stores
no extracted Markdown. It mechanically checks page boundaries, term coverage,
and reading order. Engine-specific `review` cases remain visible and never
become scientific acceptance. The separate first-user gate in
`docs/BETA_TEST.md` cannot be satisfied by smoke tests or agent simulation.

The note-quality procedure is defined in `docs/NOTE_QUALITY.md`. A reviewed
Source must declare its text basis and derived-text status, include method,
measurement, theory/model assumptions, anchored results, limitations, and a
review trace. A partial Source must declare its unread scope and must not make
broad promoted claims. An unread source uses `templates/source-capture.md` and
contains no factual summary.

Obsidian title rendering follows `docs/NOTE_QUALITY.md`: a rendered note does
not repeat its filename as a top-level heading, and the skill does not edit
`.obsidian` to hide duplicate titles. Linked Markdown basenames must also be
unique so an Obsidian wikilink has one deterministic target.

The read-only lint is necessary but not sufficient handoff evidence. Handoff
must run `scripts/check_notes.py` with `--expect-sources` set to the exact
Paper/Source count in the approved Blueprint and `--expect-profile` for a new
or upgraded preset-aware Apply. It also rejects unresolved
template placeholders, invalid text-basis values, duplicate/ambiguous note
basenames, filename-mirroring headings, and reviewed evidence-ledger items
without a type label and page anchor. For an available derivative it requires
a linked Source Text manifest with a valid hash and page-map declaration. A
mismatch fails the command. A bare run without that option is exploratory only
and cannot prove that the correct Vault or expected reference set was reviewed.
For `reviewed` sources, required dossier sections must contain substantive
content rather than `not supplied`. A promoted note must carry a PDF page
anchor and may link only to a Source dossier whose status is `reviewed`;
promotion from a partial or unread source fails.
