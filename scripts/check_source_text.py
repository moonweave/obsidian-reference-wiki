#!/usr/bin/env python3
"""Verify one approved Source Text manifest and its derived text file."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
PAGE_MARKER = re.compile(r"<!--\s*pdf-page:\s*\d+\s*-->")
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
            page_markers = len(PAGE_MARKER.findall(text))
            if metadata.get("source_text_page_map") == "pdf-page-comments" and page_markers == 0:
                errors.append("source_text_page_map declares pdf-page-comments but no page markers were found")

    return {
        "status": "pass" if not errors else "fail",
        "manifest": str(manifest),
        "derived_text": str(location) if location is not None else None,
        "byte_count": byte_count,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "page_markers": page_markers,
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
            f"{result['status']} (bytes={result['byte_count']}, page_markers={result['page_markers']})"
        )
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
