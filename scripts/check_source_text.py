#!/usr/bin/env python3
"""Verify one approved Source Text manifest and its derived text file."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
PAGE_MARKER = re.compile(r"<!--\s*pdf-page:\s*(\d+)\s*-->")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def verify(manifest: Path, vault_root: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    vault_root = vault_root.resolve()
    manifest = manifest.resolve()
    if not vault_root.is_dir():
        return {"status": "fail", "manifest": str(manifest), "errors": ["approved Vault root does not exist"]}
    if not manifest.is_relative_to(vault_root):
        return {"status": "fail", "manifest": str(manifest), "errors": ["manifest is outside the approved Vault root"]}
    if not manifest.is_file():
        return {"status": "fail", "manifest": str(manifest), "errors": ["manifest does not exist"]}
    metadata = parse_frontmatter(manifest.read_text(encoding="utf-8"))
    if metadata.get("type") != "source-text-manifest":
        errors.append("manifest type must be source-text-manifest")
    storage = metadata.get("source_text_storage", "")
    if storage not in {"external", "vault-local"}:
        errors.append("source_text_storage must be external or vault-local")
    location_value = metadata.get("source_text_location", "")
    if not location_value or location_value.lower() in {"not provided", "not supplied"}:
        errors.append("source_text_location is not supplied")
        location = None
    else:
        supplied_location = Path(location_value).expanduser()
        if storage == "external" and not supplied_location.is_absolute():
            errors.append("external source_text_location must be absolute")
        if storage == "vault-local" and supplied_location.is_absolute():
            errors.append("vault-local source_text_location must be relative to the manifest")
        location = supplied_location
        if not location.is_absolute():
            location = manifest.parent / location
        location = location.resolve()
        if storage == "vault-local" and not location.is_relative_to(vault_root):
            errors.append("vault-local derived source text is outside the approved Vault root")
            location = None
        elif not location.is_file():
            errors.append(f"derived source text does not exist: {location}")

    expected_hash = metadata.get("source_text_hash", "")
    if not SHA256.fullmatch(expected_hash):
        errors.append("source_text_hash must use sha256:<64 lowercase hex characters>")

    actual_hash = ""
    byte_count = 0
    page_markers = 0
    marker_numbers: list[int] = []
    canonical_page_count = 0
    formula_placeholders = 0
    image_placeholders = 0
    provenance_version = metadata.get("source_text_provenance_version", "")
    if provenance_version in {"1", "2"}:
        canonical_location = Path(metadata.get("canonical_location", "")).expanduser()
        if not canonical_location.is_absolute() or not canonical_location.is_file():
            errors.append("canonical_location must name an existing external PDF")
        elif canonical_location.resolve().is_relative_to(vault_root):
            errors.append("canonical PDF must remain outside the approved Vault")
        else:
            canonical_raw = canonical_location.read_bytes()
            canonical_hash = f"sha256:{hashlib.sha256(canonical_raw).hexdigest()}"
            if canonical_hash != metadata.get("canonical_source_hash", ""):
                errors.append("canonical_source_hash mismatch")
        try:
            canonical_page_count = int(metadata.get("canonical_page_count", ""))
            extracted_pages = int(metadata.get("source_text_extracted_pages", ""))
        except ValueError:
            errors.append("canonical_page_count and source_text_extracted_pages must be integers")
            extracted_pages = 0
        else:
            if canonical_page_count < 1:
                errors.append("canonical_page_count must be positive")
            if extracted_pages < 1 or extracted_pages > canonical_page_count:
                errors.append("source_text_extracted_pages is outside the canonical page range")
        for key in (
            "source_text_extractor",
            "source_text_extractor_version",
            "source_text_extraction_mode",
        ):
            if not metadata.get(key) or metadata.get(key) == "not provided":
                errors.append(f"missing {key}")
        if provenance_version == "2" and not metadata.get("source_text_extractor_options"):
            errors.append("missing source_text_extractor_options")
    elif provenance_version not in {"", "not provided"}:
        errors.append("unsupported source_text_provenance_version")
    if location is not None and location.is_file():
        raw = location.read_bytes()
        byte_count = len(raw)
        actual_hash = f"sha256:{hashlib.sha256(raw).hexdigest()}"
        if actual_hash != expected_hash:
            errors.append(f"source_text_hash mismatch: expected {expected_hash}, found {actual_hash}")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"derived source text is not valid UTF-8: {exc}")
        else:
            marker_numbers = [int(value) for value in PAGE_MARKER.findall(text)]
            page_markers = len(marker_numbers)
            formula_placeholders = text.count("<!-- formula-not-decoded -->")
            image_placeholders = text.count("<!-- image -->")
            if metadata.get("source_text_page_map") == "pdf-page-comments" and page_markers == 0:
                errors.append("source_text_page_map declares pdf-page-comments but no page markers were found")
            if provenance_version in {"1", "2"} and marker_numbers != list(range(1, canonical_page_count + 1)):
                errors.append("pdf-page markers must cover every canonical page exactly once and in order")
            if formula_placeholders:
                warnings.append(
                    f"derived text contains {formula_placeholders} undecoded formula placeholders"
                )
            if image_placeholders:
                warnings.append(
                    f"derived text contains {image_placeholders} image placeholders"
                )

    return {
        "status": "pass" if not errors else "fail",
        "manifest": str(manifest),
        "derived_text": str(location) if location is not None else None,
        "byte_count": byte_count,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "page_markers": page_markers,
        "canonical_page_count": canonical_page_count,
        "marker_numbers": marker_numbers,
        "formula_placeholders": formula_placeholders,
        "image_placeholders": image_placeholders,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--vault-root", type=Path, required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    result = verify(args.manifest.expanduser(), args.vault_root.expanduser())
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            "Source text check: "
            f"{result['status']} (bytes={result.get('byte_count', 0)}, "
            f"page_markers={result.get('page_markers', 0)})"
        )
        for error in result["errors"]:
            print(f"- {error}")
        for warning in result.get("warnings", []):
            print(f"- warning: {warning}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
