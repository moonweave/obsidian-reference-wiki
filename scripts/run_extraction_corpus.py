#!/usr/bin/env python3
"""Render and score the public source-text extraction layout corpus."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE_MARKER = re.compile(r"<!--\s*pdf-page:\s*(\d+)\s*-->")


def normalize(text: str) -> str:
    return " ".join(text.upper().split())


def split_pages(text: str) -> dict[int, str]:
    matches = list(PAGE_MARKER.finditer(text))
    pages: dict[int, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        pages[int(match.group(1))] = text[match.end():end]
    return pages


def ordered(text: str, terms: list[str]) -> bool:
    position = -1
    for term in terms:
        position = text.find(normalize(term), position + 1)
        if position < 0:
            return False
    return True


def fail(message: str, as_json: bool) -> int:
    result = {"status": "fail", "errors": [message]}
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Extraction corpus failed: {message}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--engine", choices=("pdftotext", "docling"), required=True)
    parser.add_argument("--docling-timeout-seconds", type=float, default=600.0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    corpus_path = args.corpus.expanduser().resolve()
    if not corpus_path.is_file():
        return fail(f"corpus does not exist: {corpus_path}", args.as_json)
    ps2pdf = shutil.which("ps2pdf")
    if not ps2pdf:
        return fail("required command is unavailable: ps2pdf", args.as_json)
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    fixture = (corpus_path.parent / corpus["fixture_postscript"]).resolve()
    if not fixture.is_file():
        return fail(f"PostScript fixture does not exist: {fixture}", args.as_json)

    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="reference-extraction-corpus-") as raw:
        work = Path(raw)
        canonical_pdf = work / "eight-case-corpus.pdf"
        rendered = subprocess.run(
            [ps2pdf, str(fixture), str(canonical_pdf)],
            check=False,
            capture_output=True,
            text=True,
        )
        if rendered.returncode != 0:
            return fail(rendered.stderr.strip() or "ps2pdf failed", args.as_json)
        vault = work / "vault"
        vault.mkdir()
        output = vault / "05 Source Text/Full Text/Full Text — Layout Corpus.md"
        manifest = vault / "05 Source Text/Source Text Manifest — Layout Corpus.md"
        command = [
            sys.executable,
            str(ROOT / "scripts/extract_source_text.py"),
            str(canonical_pdf),
            "--output", str(output),
            "--manifest", str(manifest),
            "--vault-root", str(vault),
            "--source-name", "Layout Corpus",
            "--reference-type", "Paper",
            "--storage", "vault-local",
            "--basis", "mixed" if args.engine == "docling" else "native-text",
            "--engine", args.engine,
            "--docling-timeout-seconds", str(args.docling_timeout_seconds),
            "--json",
        ]
        extracted = subprocess.run(
            command, check=False, capture_output=True, text=True
        )
        if extracted.returncode != 0:
            detail = extracted.stdout.strip() or extracted.stderr.strip()
            return fail(detail or "extractor failed", args.as_json)
        extraction = json.loads(extracted.stdout)
        checked = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_source_text.py"),
                str(manifest),
                "--vault-root", str(vault),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if checked.returncode != 0:
            return fail(checked.stdout.strip() or checked.stderr.strip(), args.as_json)
        integrity = json.loads(checked.stdout)
        pages = split_pages(output.read_text(encoding="utf-8"))

        case_results: list[dict[str, object]] = []
        covered_terms = 0
        total_terms = 0
        required_covered_terms = 0
        required_total_terms = 0
        for case in corpus["cases"]:
            page_text = normalize(pages.get(int(case["page"]), ""))
            missing_all = [
                term for term in case["required_terms"] if normalize(term) not in page_text
            ]
            optional_terms = set(
                case.get("docling_optional_terms", [])
                if args.engine == "docling"
                else []
            )
            missing = [term for term in missing_all if term not in optional_terms]
            total_terms += len(case["required_terms"])
            covered_terms += len(case["required_terms"]) - len(missing_all)
            required_total_terms += len(case["required_terms"]) - len(optional_terms)
            required_covered_terms += (
                len(case["required_terms"]) - len(optional_terms) - len(missing)
            )
            ordered_terms = (
                case.get("docling_ordered_terms", case["ordered_terms"])
                if args.engine == "docling"
                else case["ordered_terms"]
            )
            order_ok = ordered(page_text, ordered_terms)
            order_policy = (
                case.get("docling_order_policy", "strict")
                if args.engine == "docling"
                else "strict"
            )
            failed = bool(missing) or (not order_ok and order_policy == "strict")
            review = bool(missing_all) or (not order_ok and order_policy == "review")
            case_results.append(
                {
                    "id": case["id"],
                    "page": case["page"],
                    "status": "fail" if failed else "review" if review else "pass",
                    "missing_terms": missing,
                    "optional_missing_terms": [
                        term for term in missing_all if term in optional_terms
                    ],
                    "order_ok": order_ok,
                    "order_policy": order_policy,
                }
            )

    term_coverage = covered_terms / total_terms if total_terms else 0.0
    required_term_coverage = (
        required_covered_terms / required_total_terms if required_total_terms else 0.0
    )
    errors = [case["id"] for case in case_results if case["status"] == "fail"]
    reviews = [case["id"] for case in case_results if case["status"] == "review"]
    result = {
        "status": "pass" if not errors else "fail",
        "quality_status": "review-required" if reviews else "pass",
        "corpus_id": corpus["corpus_id"],
        "engine": args.engine,
        "extractor_version": extraction["extractor_version"],
        "case_count": len(case_results),
        "canonical_page_count": integrity["canonical_page_count"],
        "page_markers": integrity["page_markers"],
        "term_coverage": term_coverage,
        "required_term_coverage": required_term_coverage,
        "formula_placeholders": integrity["formula_placeholders"],
        "image_placeholders": integrity["image_placeholders"],
        "warnings": integrity["warnings"],
        "failed_cases": errors,
        "review_cases": reviews,
        "cases": case_results,
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"Extraction corpus: {result['status']} "
            f"(engine={args.engine}, cases={len(case_results)}, coverage={term_coverage:.3f})"
        )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
