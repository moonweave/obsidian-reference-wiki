---
name: obsidian-research-wiki-reference
description: Design, safely onboard, or extend an Obsidian reference knowledge system for papers, Zotero, citations, claims, evidence, methods, limitations, themes, and literature questions. Use for rigorous literature/reference organization, not research records or combined workspaces.
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
supplied. Evidence/Method and Limitation links are created only when supplied.
The default domains are `10 Sources`, `20 Claims`, `30 Evidence & Methods`,
`40 Limitations`, `50 Themes`, `60 Questions`, `90 Reading Queue`, and
`_templates`; do not add research-record domains.

## Existing Vault and handoff

For a mixed Vault, the baseline ledger must use exactly `keep in place`, `link
from a new note`, or `move later only with separate approval`. Do not perform a
bulk migration under a first-link approval. Before handoff, resolve every
outgoing link, confirm canonical locations remain external, report unreviewed
material, and list `.obsidian`, existing notes, source files, and plugins that
were untouched.

Propose `Reference Index`, `Sources`, `Claims`, `Evidence & Methods`, `Limitations`, `Themes`, `Questions`, `Reading Queue`, and `_templates`. A first route uses real links: `[[Reference Index]] -> [[Source — …]] -> [[Claim — …]]`. Create factual records only from supplied content or explicitly authorized reading; record canonical locations, never copies. Existing Vaults receive a read-only `keep in place` / `link from a new note` / `move later only with separate approval` ledger. Verify every wikilink resolves and report provenance, next action, and untouched material.
