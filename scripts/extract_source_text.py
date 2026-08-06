#!/usr/bin/env python3
"""Extract a PDF text layer into page-marked Markdown and a provenance manifest."""
from __future__ import annotations

import argparse
import hashlib
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def command_path(name: str) -> str:
    resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"required Poppler command is unavailable: {name}")
    return resolved


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True)


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

    pdftotext = command_path("pdftotext")
    pdfinfo = command_path("pdfinfo")
    page_count = pdf_page_count(pdfinfo, source)
    extracted_text, text_pages = extract_pages(pdftotext, source, page_count)
    version = extractor_version(pdftotext)
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
        "source_text_provenance_version": "1",
        "source_text_extractor": "pdftotext",
        "source_text_extractor_version": version,
        "source_text_extraction_mode": "layout-per-page",
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
        "extractor": "pdftotext",
        "extractor_version": version,
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
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
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
    raise SystemExit(main())
