# Reference note quality contract

Reference note quality depends on the source text and the reading trace, not on
the amount of prose in a template. The skill may use an LLM to draft Markdown
after the user supplies or authorizes the source, but it is not an automatic
PDF-ingestion or OCR pipeline.

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
   `supplied-excerpt`) and page/section numbering;
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
default. Keep the exact external canonical location and a compact review trace.

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
