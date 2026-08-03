#!/usr/bin/env python3
"""Read-only quality lint for a Reference Obsidian Vault."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
REQUIRED_SOURCE_HEADINGS = (
    "## Paper map",
    "## Abstract and scope",
    "## Method as used in this paper",
    "### Measurement and analysis",
    "## Background theory and model",
    "## Reported evidence or results",
    "### Evidence ledger",
    "## Limitations as supplied",
    "## Extraction and review trace",
)


def frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def source_notes(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if "_templates" not in path.parts
        and any(
            part in {"Sources", "Papers"}
            or part.endswith(" Sources")
            or part.endswith(" Papers")
            for part in path.parts
        )
        and path.stem.startswith(("Paper — ", "Source — "))
    )


def in_domain(path: Path, domain: str) -> bool:
    return any(part == domain or part.endswith(f" {domain}") for part in path.parts)


def check(root: Path, expected_sources: int | None = None) -> dict[str, object]:
    errors: list[str] = []
    notes = sorted(path for path in root.rglob("*.md") if "_templates" not in path.parts)
    names = {path.stem for path in notes}
    references = source_notes(root)

    for path in notes:
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if target.strip() not in names:
                errors.append(f"unresolved wikilink: {path.relative_to(root)} -> {target.strip()}")

    reviewed = 0
    partial = 0
    captured = 0
    for path in references:
        text = path.read_text(encoding="utf-8")
        meta = frontmatter(text)
        status = meta.get("status", "")
        if not meta.get("canonical_location"):
            errors.append(f"missing canonical_location: {path.relative_to(root)}")
        if status == "not reviewed":
            captured += 1
            if "Not reviewed" not in text or "## Capture reason" not in text:
                errors.append(f"invalid capture note: {path.relative_to(root)}")
            continue
        if status == "partial":
            partial += 1
        elif status == "reviewed":
            reviewed += 1
        else:
            errors.append(f"invalid source status: {path.relative_to(root)}")
        for heading in REQUIRED_SOURCE_HEADINGS:
            if heading not in text:
                errors.append(f"missing {heading}: {path.relative_to(root)}")
        for key in ("source_text_basis", "reviewed_scope", "unreviewed_scope"):
            if not meta.get(key):
                errors.append(f"missing {key}: {path.relative_to(root)}")
        if status == "reviewed":
            if not re.search(r"PDF p\.\s*\d+", text):
                errors.append(f"missing page anchor: {path.relative_to(root)}")
            if not re.search(r"\[(reported|modelled|calculated|author interpretation|synthesis)\]", text):
                errors.append(f"missing evidence type label: {path.relative_to(root)}")

    promoted = 0
    for path in notes:
        if not any(in_domain(path, folder) for folder in ("Claims", "Evidence & Methods", "Theories & Background", "Limitations")):
            continue
        promoted += 1
        text = path.read_text(encoding="utf-8")
        if "Source anchor" not in text and not re.search(r"(?:Paper|Source|Reference): \[\[", text):
            errors.append(f"promoted note lacks source provenance: {path.relative_to(root)}")

    if expected_sources is not None and len(references) != expected_sources:
        errors.append(
            f"source count mismatch: expected {expected_sources}, found {len(references)}"
        )

    return {
        "status": "pass" if not errors else "fail",
        "notes": len(notes),
        "sources": len(references),
        "expected_sources": expected_sources,
        "reviewed_sources": reviewed,
        "partial_sources": partial,
        "capture_sources": captured,
        "promoted_notes": promoted,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault", type=Path)
    parser.add_argument(
        "--expect-sources",
        type=int,
        help="fail unless the discovered Paper/Source note count matches this value",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    if args.expect_sources is not None and args.expect_sources < 0:
        parser.error("--expect-sources must be zero or greater")
    root = args.vault.expanduser().resolve()
    if not root.is_dir():
        print(f"Vault does not exist: {root}", file=sys.stderr)
        return 2
    result = check(root, expected_sources=args.expect_sources)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            "Reference note lint: "
            f"{result['status']} (sources={result['sources']}, "
            f"reviewed={result['reviewed_sources']}, partial={result['partial_sources']}, "
            f"capture={result['capture_sources']}, promoted={result['promoted_notes']})"
        )
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
