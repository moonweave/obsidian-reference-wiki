---
name: obsidian-research-wiki-reference
description: Design, safely onboard, or extend an Obsidian reference knowledge system for papers, Zotero, citations, claims, evidence, literature methods, background theories, limitations, themes, and literature questions. Use for rigorous literature/reference organization, not research records or combined workspaces.
---

# Obsidian Research Wiki: Reference

Onboard into a complete external-knowledge architecture, never a shallow starter. Design mode reads only user-authorized paths. Apply requires exact Vault path and Blueprint approval; it never changes `.obsidian`, installs plugins, copies PDFs/Zotero files, or moves existing notes.

Read [the local contract](docs/CONTRACT.md) before acting. Explain the plan in
the user's language and keep Design and Apply visibly separate.

## Installation and Vault location

If Obsidian is not installed on macOS, direct the user to the official
Obsidian download page and explain that the user installs and opens the app;
the skill does not install software. Then guide `Create new vault`, propose a
location outside Zotero storage, ask the user to confirm the exact path, and
stop before creating it. A Vault is the Markdown workspace, not a copy of the
PDF library. Do not create a second Vault if the user has an authorized one.

## First-run workflow

1. Ask for the exact Vault path, current question, and the canonical Zotero or
   PDF location. Do not choose a path or invent a source.
2. Inspect an existing Vault only after the user names it. Report the baseline
   without treating file names as facts.
3. Return a Blueprint with the complete map, note meanings, placement rules,
   labelled link rules, canonical-source boundary, first real source route,
   and a no-touch list.
4. Wait for approval of the exact path, Blueprint, and supplied source facts.
5. Apply only the approved folders, templates, and factual notes. Create an
   unread source as a capture note only when the user supplied its location;
   mark its content `not reviewed`.

## Required first path

The approved first path must be resolvable from `Reference Index` to a real
Source and then to a Claim, or explicitly stop at Source when no claim was
supplied. Evidence, Method, Theory, and Limitation links are created only when
supplied. The default domains are `10 Sources`, `20 Claims`, `30 Evidence &
Methods`, `35 Theories & Background`, `40 Limitations`, `50 Themes`, `60
Questions`, `90 Reading Queue`, and `_templates`; do not add research-record
domains.

## Method and theory boundary

`Method` in Reference means a method described or used by a paper: its purpose,
source-reported procedure, assumptions, and stated boundary. It is not the
user's own experimental protocol; Research owns that record. `Theory` means a
source-grounded background mechanism, model, or conceptual framework that is
reused across claims. Do not turn a paper's background discussion into a
scientific fact beyond what the supplied source supports.

## Paper-first capture and selective promotion

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
authorizes the source. This skill is not an automatic PDF-ingestion or OCR
pipeline. Use `source-capture.md` for an unread source; it records only the
canonical location, capture reason, and next action.

For a reviewed source, record the text basis (`native-text`, `OCR`, `mixed`, or
`supplied-excerpt`) and read in passes: paper map; method, measurements,
controls, and theory/model; results with figures/tables; then conclusion and
limitations. Preserve page/section/figure anchors, units, conditions, and
comparisons. Label each important item as `reported`, `modelled`, `calculated`,
`author interpretation`, or `synthesis`. Use `not supplied` or `not reviewed`
when the paper does not support a detail. Do not promote a node until the
Source dossier has a review trace and the relevant provenance fields.

Before handoff, run the product-local read-only lint with
`python scripts/check_notes.py <approved-vault>`. It checks Source status,
required dossier sections, page anchors, evidence-type labels, promoted-note
provenance, and resolving wikilinks; it never edits the Vault.

## Existing Vault and handoff

For a mixed Vault, the baseline ledger must use exactly `keep in place`, `link
from a new note`, or `move later only with separate approval`. Do not perform a
bulk migration under a first-link approval. Before handoff, resolve every
outgoing link, confirm canonical locations remain external, report unreviewed
material, and list `.obsidian`, existing notes, source files, and plugins that
were untouched.

Propose `Reference Index`, `Sources`, `Claims`, `Evidence & Methods`, `Theories & Background`, `Limitations`, `Themes`, `Questions`, `Reading Queue`, and `_templates`. A first route uses real links: `[[Reference Index]] -> [[Source — …]]`, then adds a Claim or promoted node only when the source supports it. Create factual records only from supplied content or explicitly authorized reading; record canonical locations, never copies. Existing Vaults receive a read-only `keep in place` / `link from a new note` / `move later only with separate approval` ledger. Verify every wikilink resolves and report provenance, next action, and untouched material.
