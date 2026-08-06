# Installation and local PDF extraction

The skill itself is Markdown, Python, and templates. It does not install
Obsidian, change `.obsidian`, or install PDF tools automatically.

## Install the Agent Skill

This repository follows the open
[Agent Skills specification](https://agentskills.io/specification). Install it
with the skill manager supported by your agent. With the portable Skills CLI:

```bash
npx skills add moonweave/obsidian-reference-wiki
```

The installer detects compatible agents and lets you choose the target and
project or global scope. To inspect the package without installing it:

```bash
npx skills add moonweave/obsidian-reference-wiki --list
```

For a manual installation, clone the repository into the skills directory
documented by your agent. The installed directory must contain `SKILL.md` at
its root and should retain the basename `obsidian-research-wiki-reference`.

Start a new agent session after installation, then ask:

```text
Use obsidian-research-wiki-reference to design a literature Vault.
```

The first response should offer `notes-only`, `searchable-library`, and
`knowledge-network` before asking for an Apply path. If another copy already
occupies the target directory, inspect it before replacing it; do not merge two
skill installations.

## Update or remove

Update a Skills CLI installation:

```bash
npx skills update obsidian-research-wiki-reference
```

Remove it from the selected agent and scope:

```bash
npx skills remove obsidian-research-wiki-reference
```

For a manual Git installation, run `git pull --ff-only` inside the installed
skill directory. Use the agent's own skill manager to disable or remove a
manual installation; skill discovery paths differ by client.

## Optional PDF extraction dependencies

Notes-only onboarding does not require Poppler or Docling. The compatible PDF
source-text extraction path requires Poppler commands:

```bash
# macOS
brew install poppler

# Debian or Ubuntu
sudo apt-get install poppler-utils
```

Verify the compatible extraction path:

```bash
pdfinfo -v
pdftotext -v
python scripts/extract_source_text.py --help
```

## Optional Docling installation

Docling is optional and runs as a separate local dependency. Follow the
[official Docling installation guide](https://docling-project.github.io/docling/getting_started/installation/).
The official package supports macOS, Linux, and Windows on x86_64 and arm64.

Install into an isolated tool environment when possible:

```bash
uv tool install docling
docling --version
```

The adapter discovers the Python interpreter named by the `docling` launcher.
If the launcher is unavailable or uses a nonstandard environment, point to the
exact executable:

```bash
export REFERENCE_DOCLING_PYTHON=/absolute/path/to/docling-environment/bin/python
```

Docling may download model files on its first use. The adapter disables remote
services and external plugins during conversion; the canonical PDF and derived
Markdown remain local. Installing Docling does not authorize extracting a PDF.

## Extraction profiles

Use the compatibility path for a simple PDF text layer:

```bash
python scripts/extract_source_text.py /absolute/source.pdf \
  --output /absolute/vault/05\ Source\ Text/Full\ Text/full.md \
  --manifest /absolute/vault/05\ Source\ Text/manifest.md \
  --vault-root /absolute/vault --source-name "Short title" \
  --reference-type Paper --storage vault-local \
  --basis native-text --engine pdftotext
```

Use Docling for complex layout. OCR and formula enrichment remain off unless
explicitly requested:

```bash
python scripts/extract_source_text.py /absolute/source.pdf \
  --output /absolute/vault/05\ Source\ Text/Full\ Text/full.md \
  --manifest /absolute/vault/05\ Source\ Text/manifest.md \
  --vault-root /absolute/vault --source-name "Short title" \
  --reference-type Paper --storage vault-local \
  --basis mixed --engine docling --docling-timeout-seconds 600
```

Recover formulas only on reviewed pages when possible:

```bash
--docling-formula-pages 2,4-6
```

Use `--docling-formula on` only for an intentional full-document enrichment
pass. Do not combine it with `--docling-formula-pages`. A timeout fails without
writing the final derivative or manifest.

## Public extraction corpus

Ghostscript is required only to render the repository-owned quality fixture:

```bash
# macOS
brew install ghostscript

# Debian or Ubuntu
sudo apt-get install ghostscript

python scripts/run_extraction_corpus.py \
  --corpus evals/corpus/source-text-extraction/corpus.json \
  --engine pdftotext --json
```

The Docling comparison is optional. A `review-required` quality status names
known parser limitations; it is not a scientific acceptance verdict.
