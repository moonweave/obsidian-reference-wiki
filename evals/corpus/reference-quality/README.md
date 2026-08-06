# Reference source-to-dossier quality corpus

This fixed corpus connects a rendered two-page PDF to explicit dossier facts.
It measures whether a candidate preserves the reported values, units,
condition, baseline, repeatability boundary, next action, evidence labels, and
PDF page anchors. The unsupported candidate deliberately changes 12 mA to 20
mA and reverses the repeatability boundary.

Run:

```bash
python scripts/score_dossier.py \
  --corpus evals/corpus/reference-quality/corpus.json \
  --dossier evals/corpus/reference-quality/candidates/good.md --json
```

This deterministic corpus is a minimum semantic regression, not a substitute
for human review or a broader scientific-paper benchmark.
