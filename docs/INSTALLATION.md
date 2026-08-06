# Installation and local PDF extraction

The skill itself is Markdown, Python, and templates. It does not install
Obsidian, change `.obsidian`, or install PDF tools automatically.

## Install the Codex skill

Git and Codex are the only requirements for notes-only use. Install the public
repository directly under the Codex skill directory.

macOS or Linux:

```bash
mkdir -p "$HOME/.codex/skills"
git clone https://github.com/moonweave/obsidian-reference-wiki.git \
  "$HOME/.codex/skills/obsidian-research-wiki-reference"
test -f "$HOME/.codex/skills/obsidian-research-wiki-reference/SKILL.md"
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME/.codex/skills" | Out-Null
git clone https://github.com/moonweave/obsidian-reference-wiki.git `
  "$HOME/.codex/skills/obsidian-research-wiki-reference"
Test-Path "$HOME/.codex/skills/obsidian-research-wiki-reference/SKILL.md"
```

Start a new Codex session after installation. A direct first invocation is:

```text
$obsidian-research-wiki-reference Help me design a literature Vault. Do not create files yet.
```

The first response should offer `notes-only`, `searchable-library`, and
`knowledge-network` before asking for an Apply path. If another copy already
occupies the target directory, inspect it before replacing it; do not merge two
skill installations.

## Update or disable

Update a Git-based installation:

```bash
git -C "$HOME/.codex/skills/obsidian-research-wiki-reference" pull --ff-only
```

To disable the skill without deleting it, close Codex and move it outside the
active basename:

```bash
mv "$HOME/.codex/skills/obsidian-research-wiki-reference" \
  "$HOME/.codex/skills/obsidian-research-wiki-reference.disabled"
```

On PowerShell, use `Rename-Item` with the same source and `.disabled`
destination. Move it back to the original basename to re-enable it.

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
