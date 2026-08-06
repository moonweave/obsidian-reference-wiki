#!/usr/bin/env python3
"""Extract a PDF text layer into page-marked Markdown and a provenance manifest."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = re.compile(r"\{[a-z_][a-z0-9_]*\}")
PAGES = re.compile(r"^Pages:\s+(\d+)\s*$", re.MULTILINE)
PAGE_BREAK_TOKEN = "<<<REFERENCE_WIKI_PDF_PAGE_BREAK>>>"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def command_path(name: str) -> str:
    resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"required command is unavailable: {name}")
    return resolved


def run(
    command: list[str], timeout: float | None = None
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Docling extraction timed out after {timeout:g} seconds"
        ) from exc


def pdf_page_count(pdfinfo: str, source: Path) -> int:
    result = run([pdfinfo, str(source)])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "pdfinfo failed")
    match = PAGES.search(result.stdout)
    if not match:
        raise RuntimeError("pdfinfo did not report a page count")
    return int(match.group(1))


def extractor_version(pdftotext: str) -> str:
    result = run([pdftotext, "-v"])
    text = (result.stderr or result.stdout).strip().splitlines()
    return text[0].strip() if text else "pdftotext version unknown"


def normalize_page(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\f", "").splitlines()]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def parse_page_selection(value: str, page_count: int) -> list[int]:
    selected: set[int] = set()
    for raw_part in value.split(","):
        part = raw_part.strip()
        if not part:
            raise RuntimeError("--docling-formula-pages contains an empty item")
        match = re.fullmatch(r"(\d+)(?:-(\d+))?", part)
        if not match:
            raise RuntimeError(
                "--docling-formula-pages must use page numbers and ranges such as 2,4-6"
            )
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if start > end:
            raise RuntimeError("--docling-formula-pages ranges must be ascending")
        if start < 1 or end > page_count:
            raise RuntimeError(
                f"--docling-formula-pages must stay within PDF pages 1-{page_count}"
            )
        selected.update(range(start, end + 1))
    return sorted(selected)


def format_page_selection(pages: list[int]) -> str:
    ranges: list[str] = []
    start = previous = pages[0]
    for page in pages[1:]:
        if page == previous + 1:
            previous = page
            continue
        ranges.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = page
    ranges.append(str(start) if start == previous else f"{start}-{previous}")
    return ",".join(ranges)


def extract_pages(pdftotext: str, source: Path, page_count: int) -> tuple[str, int]:
    rendered: list[str] = []
    text_pages = 0
    for page in range(1, page_count + 1):
        result = run(
            [
                pdftotext,
                "-f", str(page),
                "-l", str(page),
                "-layout",
                "-nopgbrk",
                "-enc", "UTF-8",
                str(source),
                "-",
            ]
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"pdftotext failed on page {page}")
        page_text = normalize_page(result.stdout)
        if page_text:
            text_pages += 1
        rendered.append(f"<!-- pdf-page: {page} -->\n{page_text}".rstrip())
    if text_pages == 0:
        raise RuntimeError(
            "the PDF has no extractable text layer; create an authorized OCR derivative first"
        )
    return "\n\n".join(rendered) + "\n", text_pages


def docling_python() -> str:
    override = os.environ.get("REFERENCE_DOCLING_PYTHON", "").strip()
    if override:
        interpreter = Path(override).expanduser().absolute()
        if not interpreter.is_file() or not os.access(interpreter, os.X_OK):
            raise RuntimeError(f"REFERENCE_DOCLING_PYTHON is not executable: {interpreter}")
        return str(interpreter)
    if importlib.util.find_spec("docling") is not None:
        return sys.executable
    command = Path(command_path("docling")).resolve()
    try:
        first_line = command.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, UnicodeDecodeError, IndexError) as exc:
        raise RuntimeError(f"cannot inspect the Docling launcher: {command}") from exc
    if not first_line.startswith("#!"):
        raise RuntimeError(
            "cannot determine Docling's Python environment; set REFERENCE_DOCLING_PYTHON"
        )
    # Keep a virtual-environment symlink intact: resolving it can bypass that
    # environment's site-packages and make an installed Docling disappear.
    interpreter = Path(first_line[2:].strip()).expanduser().absolute()
    if not interpreter.is_file() or not os.access(interpreter, os.X_OK):
        raise RuntimeError(f"Docling Python is not executable: {interpreter}")
    return str(interpreter)


def docling_pass(
    interpreter: str,
    source: Path,
    ocr_mode: str,
    formula_mode: str,
    timeout_seconds: float,
    page_start: int,
    page_end: int,
) -> tuple[list[str], str]:
    with tempfile.TemporaryDirectory() as raw:
        temporary = Path(raw)
        markdown_path = temporary / "docling.md"
        metadata_path = temporary / "docling.json"
        result = run(
            [
                interpreter,
                str(Path(__file__).resolve()),
                "--docling-worker",
                str(source),
                "--output", str(markdown_path),
                "--metadata", str(metadata_path),
                "--ocr", ocr_mode,
                "--formula", formula_mode,
                "--page-start", str(page_start),
                "--page-end", str(page_end),
            ],
            timeout=timeout_seconds,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise RuntimeError(detail or "Docling extraction failed")
        if not markdown_path.is_file() or not metadata_path.is_file():
            raise RuntimeError("Docling worker did not create its expected outputs")
        markdown = markdown_path.read_text(encoding="utf-8")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    pages = [normalize_page(part) for part in markdown.split(PAGE_BREAK_TOKEN)]
    expected_pages = page_end - page_start + 1
    if len(pages) != expected_pages:
        raise RuntimeError(
            f"Docling page boundary mismatch: expected {expected_pages}, found {len(pages)}"
        )
    return pages, str(metadata["version"])


def extract_docling(
    source: Path,
    page_count: int,
    ocr_mode: str,
    formula_mode: str,
    formula_pages: list[int],
    timeout_seconds: float,
) -> tuple[str, int, str, str]:
    interpreter = docling_python()
    base_formula_mode = "off" if formula_pages else formula_mode
    pages, version = docling_pass(
        interpreter,
        source,
        ocr_mode,
        base_formula_mode,
        timeout_seconds,
        1,
        page_count,
    )
    if formula_pages:
        page_start = formula_pages[0]
        page_end = formula_pages[-1]
        enriched, enriched_version = docling_pass(
            interpreter,
            source,
            ocr_mode,
            "on",
            timeout_seconds,
            page_start,
            page_end,
        )
        if enriched_version != version:
            raise RuntimeError("Docling version changed between extraction passes")
        for page_number in formula_pages:
            pages[page_number - 1] = enriched[page_number - page_start]
    text_pages = sum(bool(page) for page in pages)
    if text_pages == 0:
        raise RuntimeError("Docling produced no readable page content")
    rendered = [f"<!-- pdf-page: {index} -->\n{page}".rstrip() for index, page in enumerate(pages, 1)]
    formula_setting = (
        f"selected:{format_page_selection(formula_pages)}"
        if formula_pages
        else str(formula_mode == "on").lower()
    )
    options = (
        f"pipeline=standard;ocr={ocr_mode};formula_enrichment={formula_setting};"
        f"timeout_seconds_per_pass={timeout_seconds:g};remote_services=false;"
        "external_plugins=false;page_breaks=pdf-page-comments"
    )
    return "\n\n".join(rendered) + "\n", text_pages, version, options


def docling_worker(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--ocr", choices=("auto", "off"), required=True)
    parser.add_argument("--formula", choices=("on", "off"), required=True)
    parser.add_argument("--page-start", type=int, required=True)
    parser.add_argument("--page-end", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        import docling
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption

        options = PdfPipelineOptions()
        options.do_ocr = args.ocr == "auto"
        options.do_formula_enrichment = args.formula == "on"
        options.enable_remote_services = False
        options.allow_external_plugins = False
        converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
        )
        result = converter.convert(
            args.source, page_range=(args.page_start, args.page_end)
        )
        markdown = result.document.export_to_markdown(
            page_break_placeholder=PAGE_BREAK_TOKEN,
            traverse_pictures=True,
        )
        version = getattr(docling, "__version__", None) or importlib.metadata.version("docling")
        args.output.write_text(markdown, encoding="utf-8")
        args.metadata.write_text(
            json.dumps({"version": version}, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as exc:
        print(f"Docling worker failed: {exc}", file=sys.stderr)
        return 1
    return 0


def render(template: Path, values: dict[str, str]) -> str:
    text = template.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
    unresolved = PLACEHOLDER.findall(text)
    if unresolved:
        raise RuntimeError(f"unresolved template fields in {template.name}: {sorted(set(unresolved))}")
    return text


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        stream.write(content)
        temporary = Path(stream.name)
    temporary.replace(path)


def extract(args: argparse.Namespace) -> dict[str, object]:
    source = args.pdf.expanduser().resolve()
    output = args.output.expanduser().resolve()
    manifest = args.manifest.expanduser().resolve()
    vault_root = args.vault_root.expanduser().resolve()
    if not source.is_file():
        raise RuntimeError(f"canonical PDF does not exist: {source}")
    if source.suffix.lower() != ".pdf":
        raise RuntimeError("canonical source must be a PDF")
    if not vault_root.is_dir():
        raise RuntimeError(f"approved Vault root does not exist: {vault_root}")
    if source == vault_root or vault_root in source.parents:
        raise RuntimeError("canonical PDF must remain outside the approved Vault")
    if not manifest.is_relative_to(vault_root):
        raise RuntimeError("manifest must be inside the approved Vault")
    if args.storage == "vault-local" and not output.is_relative_to(vault_root):
        raise RuntimeError("vault-local output must be inside the approved Vault")
    if args.storage == "external" and output.is_relative_to(vault_root):
        raise RuntimeError("external output must be outside the approved Vault")
    if output == manifest:
        raise RuntimeError("output and manifest paths must differ")
    for path in (output, manifest):
        if path.exists() and not args.overwrite:
            raise RuntimeError(f"refusing to overwrite existing file: {path}")

    pdfinfo = command_path("pdfinfo")
    page_count = pdf_page_count(pdfinfo, source)
    formula_pages = (
        parse_page_selection(args.docling_formula_pages, page_count)
        if args.docling_formula_pages
        else []
    )
    if args.engine == "docling":
        if args.basis != "mixed":
            raise RuntimeError("Docling extraction must use --basis mixed")
        extracted_text, text_pages, version, extractor_options = extract_docling(
            source,
            page_count,
            args.docling_ocr,
            args.docling_formula,
            formula_pages,
            args.docling_timeout_seconds,
        )
        extractor = "docling"
        extraction_mode = "docling-standard-page-marked"
    else:
        pdftotext = command_path("pdftotext")
        extracted_text, text_pages = extract_pages(pdftotext, source, page_count)
        version = extractor_version(pdftotext)
        extractor_options = "-layout -nopgbrk -enc UTF-8 per-page"
        extractor = "pdftotext"
        extraction_mode = "layout-per-page"
    canonical_hash = sha256(source)
    location = (
        os.path.relpath(output, manifest.parent)
        if args.storage == "vault-local"
        else str(output)
    )
    values = {
        "canonical_location": str(source),
        "canonical_source_hash": canonical_hash,
        "canonical_page_count": str(page_count),
        "source_text_basis": args.basis,
        "source_text_page_map": "pdf-page-comments",
        "source_text_provenance_version": "2",
        "source_text_extractor": extractor,
        "source_text_extractor_version": version,
        "source_text_extractor_options": extractor_options,
        "source_text_extraction_mode": extraction_mode,
        "source_text_extracted_pages": str(text_pages),
        "full_text_content": extracted_text.rstrip(),
    }
    template_root = ROOT / "templates"
    if not (template_root / "full-text.md").is_file():
        template_root = template_root / "reference"
    derivative = render(template_root / "full-text.md", values)
    derivative_hash = f"sha256:{hashlib.sha256(derivative.encode('utf-8')).hexdigest()}"
    manifest_values = values | {
        "source_text_status": "available",
        "reference_type": args.reference_type,
        "source_name": args.source_name,
        "source_text_storage": args.storage,
        "source_text_location": location,
        "source_text_hash": derivative_hash,
    }
    manifest_text = render(template_root / "source-text-manifest.md", manifest_values)
    atomic_write(output, derivative)
    atomic_write(manifest, manifest_text)
    return {
        "status": "pass",
        "canonical_pdf": str(source),
        "canonical_source_hash": canonical_hash,
        "output": str(output),
        "manifest": str(manifest),
        "storage": args.storage,
        "pages": page_count,
        "text_pages": text_pages,
        "source_text_hash": derivative_hash,
        "extractor": extractor,
        "extractor_version": version,
        "extractor_options": extractor_options,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--vault-root", type=Path, required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--reference-type", choices=("Paper", "Source"), required=True)
    parser.add_argument("--storage", choices=("vault-local", "external"), required=True)
    parser.add_argument("--basis", choices=("native-text", "OCR", "mixed"), required=True)
    parser.add_argument(
        "--engine",
        choices=("pdftotext", "docling"),
        default=os.environ.get("REFERENCE_PDF_ENGINE", "pdftotext"),
    )
    parser.add_argument("--docling-ocr", choices=("auto", "off"), default="off")
    parser.add_argument("--docling-formula", choices=("on", "off"), default="off")
    parser.add_argument("--docling-formula-pages", default="")
    parser.add_argument("--docling-timeout-seconds", type=float, default=600.0)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        if args.engine not in ("pdftotext", "docling"):
            raise RuntimeError(
                "REFERENCE_PDF_ENGINE must be either 'pdftotext' or 'docling'"
            )
        if args.docling_timeout_seconds <= 0:
            raise RuntimeError("--docling-timeout-seconds must be positive")
        if args.docling_formula_pages and args.engine != "docling":
            raise RuntimeError("--docling-formula-pages requires --engine docling")
        if args.docling_formula_pages and args.docling_formula == "on":
            raise RuntimeError(
                "use either --docling-formula on or --docling-formula-pages, not both"
            )
        result = extract(args)
    except RuntimeError as exc:
        if args.as_json:
            print(json.dumps({"status": "fail", "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        else:
            print(f"Source text extraction failed: {exc}", file=sys.stderr)
        return 1
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            "Source text extraction: pass "
            f"(pages={result['pages']}, text_pages={result['text_pages']})"
        )
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--docling-worker":
        raise SystemExit(docling_worker(sys.argv[2:]))
    raise SystemExit(main())
