# Reference contract

`contract_version: 6`

Reference owns external knowledge: source provenance, claims, evidence,
literature methods, background theories, limitations, themes, questions, and
reading queue. It does not own the user's experiment history, raw data, code,
or next research decision.

Design mode is read-only and limited to paths the user names. Apply requires
an exact Vault path and an approved Blueprint. The default mutation set is
folders, approved templates, and supplied factual notes. `.obsidian`, plugins,
bulk moves, renames, deletes, and copies of source material remain out of
scope.

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
Markdown or text derivative is an immutable reading input, stored outside the
Vault by default. `Source Text — …` is a manifest for that derivative; it
records `source_text_location`, `source_text_basis`, `source_text_hash`, and
`source_text_page_map`, but it is not a summary or a Claim. If no derivative
was supplied, record `source_text_status: not supplied` and do not create an
empty placeholder file.

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
Paper/Source count in the approved Blueprint. It also rejects unresolved
template placeholders, invalid text-basis values, duplicate/ambiguous note
basenames, filename-mirroring headings, and reviewed evidence-ledger items
without a type label and page anchor. For an available derivative it requires
a linked Source Text manifest with a valid hash and page-map declaration. A
mismatch fails the command. A bare run without that option is exploratory only
and cannot prove that the correct Vault or expected reference set was reviewed.
