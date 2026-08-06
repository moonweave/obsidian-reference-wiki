# Reference onboarding interview

Onboarding discovers how the researcher retrieves knowledge and where a full
text derivative can safely live. It does not reduce the Reference architecture
or ask the user to make every implementation decision.

## Stage 1 — depth preset and safety context

Start with one plain-language choice. Recommend `searchable-library` when the
user is unsure.

| Preset | User-facing meaning | Internal mapping |
|---|---|---|
| `notes-only` | Reviewed Paper/Source notes. Do not create or import a full-text derivative. | `paper-first`; policy `omit`; storage `not-applicable`. |
| `searchable-library` | Reviewed notes plus searchable parsed/OCR full text for recall and verification. | `balanced`; `vault-local` or `external` after the safety check. |
| `knowledge-network` | Searchable full text and reviewed dossiers plus selectively promoted Claim/Method/Theory/Evidence/Limitation/Theme notes. | `concept-network`; `vault-local` or `external` after the safety check. |

The three presets are cumulative in capability, not three different schemas.
The full-text derivative improves search and verification; it is not itself a
deeper knowledge note or raw truth. Every preset retains Paper/Source dossiers,
and promotion remains selective even in `knowledge-network`.

After the preset choice, ask only for missing safety and source facts:

1. Is the Vault private, shared with collaborators, or published, and is its
   synchronization exposure `none`, `controlled`, `public`, or `uncertain`?
2. Where are Zotero items, PDFs, parsed/OCR Markdown, and any existing Obsidian
   notes currently kept? Is a derivative available and authorized for this
   pilot?

Storage remains independent from knowledge depth. Record availability
separately from policy and storage. Use `vault-local` only for a
private or controlled Vault that selected searchable full text. Use `external`
for shared, published, publicly synchronized, or uncertain Vaults. Use `not
supplied` and `preset_status: pending-source-text` when a searchable preset has
no authorized derivative. Use `not-applicable` for `notes-only`. Never delete
or move an existing derivative because the user chose a shallower preset.

Use the product-local read-only helper to make the mapping deterministic:

```bash
python scripts/recommend_profile.py \
  --preset searchable-library \
  --sharing private \
  --sync-exposure none \
  --derived-text available
```

The legacy `--retrieval` plus `--full-text-search` interface remains available
for existing callers, but new onboarding leads with a preset. The helper
recommends; it does not inspect a Vault or create files. Explain the mapping in
the user's language and let the user revise it.

## Recommendation response

Return one recommendation before asking for file approval:

```text
Selected preset: <notes-only | searchable-library | knowledge-network>
Recommended configuration: <organization> + <source-text storage>
Source-text policy and availability: <policy> + <availability>
Preset status: <ready | pending-source-text>
Why: <retrieval and safety rationale>
Meaningful alternative: <one alternative and its trade-off>
No files have been created or changed.
```

Do not hide the storage consequence. `vault-local` makes full text available
to Obsidian and local agents but can increase Vault size and accidental sharing
risk. `external` keeps the knowledge Vault smaller and safer to share but may
reduce portability and Obsidian-native full-text search.
Public or uncertain synchronization exposure overrides a private-use label and
requires `external`; controlled private synchronization does not override the
other answers but must be named in the Blueprint.

## Stage 2 — execution approval

After the user accepts or adjusts the recommendation, confirm:

1. Is this a new or existing Vault, and what is the exact Vault path?
2. What is the first Apply scope? Recommend one to three supplied sources as a
   pilot; do not fold a library-wide migration into onboarding.
3. Which existing folders, basenames, links, `.obsidian` settings, plugins,
   synchronization rules, and publication boundaries must remain untouched?

For an existing authorized Vault, inspect read-only and classify candidates as
`keep in place`, `link from a new note`, or `move later only with separate
approval`.

## Blueprint handoff

The Blueprint must state:

- selected depth preset and evidence;
- mapped organization and source-text storage modes;
- source-text policy, availability, preset status, and next action;
- one persisted `Reference Profile` linked from `Reference Index`;
- exact folders and templates proposed;
- canonical PDF/Zotero boundary;
- vault-local cache or external derivative location rule;
- the first real `Reference Index -> Paper/Source` route and any justified
  promoted links;
- exact Apply scope and expected Paper/Source count;
- no-touch list and sharing/publication warning; and
- the approval sentence the user can accept or revise.

Design mode ends here. Apply starts only after the exact path and Blueprint are
approved.
