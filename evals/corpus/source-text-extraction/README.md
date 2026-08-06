# Source-text extraction layout corpus

This deterministic corpus renders eight layout cases from the repository-owned
PostScript fixture into a temporary PDF. It checks page markers, required terms,
and reading order without committing a generated PDF or extracted Markdown.

Cases cover single-column text, two columns, equation-like text, a ruled table,
header/footer separation, sparse placement, rotated text, and a graphic with a
caption. This is a parser regression corpus, not evidence that scientific
equations or figures are semantically correct.

Run the fast compatibility gate:

```bash
python scripts/run_extraction_corpus.py \
  --corpus evals/corpus/source-text-extraction/corpus.json \
  --engine pdftotext --json
```

Run the optional local Docling comparison:

```bash
python scripts/run_extraction_corpus.py \
  --corpus evals/corpus/source-text-extraction/corpus.json \
  --engine docling --docling-timeout-seconds 600 --json
```

The runner requires `ps2pdf` to build its temporary canonical PDF. Docling is
required only for the Docling comparison. Quality warnings remain visible in
the JSON and are not converted into scientific acceptance.
