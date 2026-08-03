# Reference onboarding interview

Onboarding discovers how the researcher retrieves knowledge and where a full
text derivative can safely live. It does not reduce the Reference architecture
or ask the user to make every implementation decision.

## Stage 1 — style diagnosis

Ask only for missing answers. Present the four questions together when the
user is starting from scratch; otherwise acknowledge supplied answers and ask
only the unresolved decision.

1. What should be easiest to retrieve: one paper's complete contents,
   cross-paper concepts, or both?
2. Should an agent or Obsidian search and reread the full parsed/OCR text, or
   are reviewed Paper/Source dossiers sufficient?
3. Is the Vault private, shared with collaborators, published, or synchronized
   through a repository that may expose files?
4. Where are Zotero items, PDFs, parsed/OCR Markdown, and any existing Obsidian
   notes currently kept?

Translate the answers into two independent recommendations:

| Axis | Choice | Recommend when |
|---|---|---|
| Knowledge organization | `paper-first` | The researcher primarily revisits individual papers. |
| Knowledge organization | `balanced` | Both paper recall and cross-paper synthesis matter; use this when unsure. |
| Knowledge organization | `concept-network` | Cross-paper Claim/Theory/Method retrieval is primary, while each dossier remains authoritative. |
| Source-text storage | `vault-local` | The Vault is private and full-text agent/Obsidian search is valuable. |
| Source-text storage | `external` | The Vault is shared/published or source-text exposure and synchronization are concerns. |
| Source-text storage | `not supplied` | No authorized derivative exists; create no empty cache. |

Promotion remains selective in every organization mode. `concept-network`
changes the promotion threshold, not the provenance requirement, and never
replaces the Paper/Source dossier.

After the four answers are known, use the product-local read-only helper to
make the default deterministic:

```bash
python scripts/recommend_profile.py \
  --retrieval both \
  --full-text-search required \
  --sharing private \
  --derived-text available
```

The helper recommends; it does not inspect a Vault or create files. Explain
the recommendation in the user's language and let the user revise it.

## Recommendation response

Return one recommendation before asking for file approval:

```text
Style diagnosis: <short evidence from the answers>
Recommended configuration: <organization> + <source-text storage>
Why: <retrieval and safety rationale>
Meaningful alternative: <one alternative and its trade-off>
No files have been created or changed.
```

Do not hide the storage consequence. `vault-local` makes full text available
to Obsidian and local agents but can increase Vault size and accidental sharing
risk. `external` keeps the knowledge Vault smaller and safer to share but may
reduce portability and Obsidian-native full-text search.

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

- diagnosed retrieval style and evidence;
- recommended organization and source-text storage modes;
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
