#!/usr/bin/env python3
"""Score a Reference dossier against a fixed source-grounded corpus."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def file_hash(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def score(corpus_path: Path, dossier_path: Path) -> dict[str, object]:
    corpus_path = corpus_path.expanduser().resolve()
    dossier_path = dossier_path.expanduser().resolve()
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    source_pdf = (corpus_path.parent / corpus["source_pdf"]).resolve()
    errors: list[str] = []
    if not source_pdf.is_file():
        errors.append(f"source PDF is missing: {source_pdf}")
    elif file_hash(source_pdf) != corpus["source_sha256"]:
        errors.append("source PDF hash mismatch")
    if not dossier_path.is_file():
        errors.append(f"dossier is missing: {dossier_path}")
        text = ""
    else:
        text = dossier_path.read_text(encoding="utf-8")

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    matched: list[str] = []
    anchored: list[str] = []
    quantitative_total = 0
    quantitative_matched = 0
    for fact in corpus["facts"]:
        if fact.get("quantitative"):
            quantitative_total += 1
        matching_lines = [
            line for line in lines
            if all(term.casefold() in line.casefold() for term in fact["terms"])
        ]
        if not matching_lines:
            continue
        matched.append(fact["id"])
        if fact.get("quantitative"):
            quantitative_matched += 1
        expected_anchor = re.compile(rf"\bPDF p\.\s*{fact['page']}\b", re.IGNORECASE)
        expected_label = f"[{fact['label']}]".casefold()
        if any(expected_anchor.search(line) and expected_label in line.casefold() for line in matching_lines):
            anchored.append(fact["id"])

    fact_count = len(corpus["facts"])
    fact_coverage = len(matched) / fact_count if fact_count else 1.0
    anchor_accuracy = len(anchored) / len(matched) if matched else 0.0
    quantitative_retention = (
        quantitative_matched / quantitative_total if quantitative_total else 1.0
    )
    unsupported_matches: list[str] = []
    for pattern in corpus["unsupported_patterns"]:
        unsupported_matches.extend(re.findall(pattern, text, re.IGNORECASE))
    missing_sections = [
        heading for heading in corpus["required_sections"] if heading not in text
    ]
    missing_facts = [
        fact["id"] for fact in corpus["facts"] if fact["id"] not in matched
    ]
    if missing_sections:
        errors.append("missing required dossier sections")
    if fact_coverage < 1.0:
        errors.append("required source facts are missing or altered")
    if anchor_accuracy < 1.0:
        errors.append("matched facts lack the expected label or PDF page anchor")
    if unsupported_matches:
        errors.append("unsupported or contradicted claims were detected")

    return {
        "status": "pass" if not errors else "fail",
        "corpus_id": corpus["corpus_id"],
        "source_pdf": str(source_pdf),
        "dossier": str(dossier_path),
        "fact_coverage": round(fact_coverage, 4),
        "anchor_accuracy": round(anchor_accuracy, 4),
        "quantitative_retention": round(quantitative_retention, 4),
        "unsupported_claims": len(unsupported_matches),
        "matched_facts": matched,
        "missing_facts": missing_facts,
        "missing_sections": missing_sections,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--dossier", type=Path, required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    result = score(args.corpus, args.dossier)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            "Reference dossier score: "
            f"{result['status']} (coverage={result['fact_coverage']}, "
            f"anchors={result['anchor_accuracy']}, unsupported={result['unsupported_claims']})"
        )
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
