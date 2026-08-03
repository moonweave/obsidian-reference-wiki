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
PLACEHOLDER = re.compile(r"\{[a-z_][a-z0-9_]*\}")
TOP_LEVEL_HEADING = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
EVIDENCE_LABEL = re.compile(r"\[(reported|modelled|calculated|author interpretation|synthesis)\]")
PAGE_ANCHOR = re.compile(r"\bPDF pp?\.\s*\d+")
VALID_TEXT_BASES = {"native-text", "OCR", "mixed", "supplied-excerpt"}
VALID_SOURCE_TEXT_STATUSES = {"available", "not supplied", "not reviewed", "stale"}
VALID_PAGE_MAPS = {"pdf-page-comments", "section-only", "not provided"}
SOURCE_TEXT_HASH = re.compile(r"^sha256:[0-9a-f]{64}$")
SOURCE_TEXT_MANIFEST_TYPE = "source-text-manifest"
REQUIRED_SOURCE_HEADINGS = (
    "## Paper map",
    "## Abstract and scope",
    "## Method as used in this paper",
    "### Measurement and analysis",
    "## Background theory and model",
    "## Reported evidence or results",
    "### Evidence ledger",
    "## Limitations as supplied",
    "## Derived source text",
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


def not_provided(value: str) -> bool:
    return value.strip().lower() in {"", "not provided", "not supplied", "unknown"}


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


def evidence_bullets(section: str) -> list[str]:
    bullets: list[str] = []
    current = ""
    for line in section.splitlines():
        if re.match(r"^\s*-\s+", line):
            if current:
                bullets.append(current)
            current = line.strip()
        elif current and line.strip():
            current += f" {line.strip()}"
    if current:
        bullets.append(current)
    return bullets


def check(root: Path, expected_sources: int | None = None) -> dict[str, object]:
    errors: list[str] = []
    notes = sorted(path for path in root.rglob("*.md") if "_templates" not in path.parts)
    name_paths: dict[str, list[Path]] = {}
    for path in notes:
        name_paths.setdefault(path.stem, []).append(path)
    references = source_notes(root)

    for name, paths in sorted(name_paths.items()):
        if len(paths) > 1:
            locations = ", ".join(str(path.relative_to(root)) for path in paths)
            errors.append(f"duplicate Markdown basename: {name} ({locations})")

    for path in notes:
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER.search(path.stem) or PLACEHOLDER.search(text):
            errors.append(f"unresolved template placeholder: {path.relative_to(root)}")
        if any(heading.strip() == path.stem for heading in TOP_LEVEL_HEADING.findall(text)):
            errors.append(f"filename-mirroring top-level heading: {path.relative_to(root)}")
        for target in LINK.findall(text):
            target = target.strip()
            candidates = name_paths.get(target, [])
            if not candidates:
                errors.append(f"unresolved wikilink: {path.relative_to(root)} -> {target.strip()}")
            elif len(candidates) > 1:
                locations = ", ".join(str(candidate.relative_to(root)) for candidate in candidates)
                errors.append(f"ambiguous wikilink: {path.relative_to(root)} -> {target} ({locations})")

    manifests = [
        path
        for path in notes
        if frontmatter(path.read_text(encoding="utf-8")).get("type") == SOURCE_TEXT_MANIFEST_TYPE
    ]
    manifest_names = {path.stem for path in manifests}
    manifest_sources: dict[str, str] = {}
    manifest_metadata: dict[str, dict[str, str]] = {}
    for path in manifests:
        text = path.read_text(encoding="utf-8")
        meta = frontmatter(text)
        manifest_metadata[path.stem] = meta
        relative = path.relative_to(root)
        if meta.get("status") not in {"available", "stale"}:
            errors.append(f"invalid source-text manifest status: {relative}")
        for key in (
            "canonical_location",
            "source_text_location",
            "source_text_basis",
            "source_text_hash",
            "source_text_page_map",
        ):
            if not meta.get(key):
                errors.append(f"missing {key}: {relative}")
        if meta.get("source_text_basis") not in VALID_TEXT_BASES:
            errors.append(f"invalid source_text_basis: {relative} -> {meta.get('source_text_basis', '')}")
        if meta.get("source_text_page_map") not in VALID_PAGE_MAPS:
            errors.append(f"invalid source_text_page_map: {relative} -> {meta.get('source_text_page_map', '')}")
        if not SOURCE_TEXT_HASH.fullmatch(meta.get("source_text_hash", "")):
            errors.append(f"invalid source_text_hash: {relative}")
        source_targets = [
            target.strip()
            for target in LINK.findall(text)
            if target.strip().startswith(("Paper — ", "Source — "))
        ]
        if len(source_targets) != 1:
            errors.append(f"source-text manifest must link exactly one Paper/Source: {relative}")
        else:
            manifest_sources[path.stem] = source_targets[0]

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
            if meta.get("source_text_status") not in {"not reviewed", "not supplied"}:
                errors.append(f"invalid source_text_status: {path.relative_to(root)}")
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
        source_text_status = meta.get("source_text_status", "")
        if source_text_status not in VALID_SOURCE_TEXT_STATUSES:
            errors.append(f"invalid source_text_status: {path.relative_to(root)} -> {source_text_status or 'missing'}")
        for key in ("source_text_location", "source_text_hash", "source_text_page_map", "source_text_manifest"):
            if not meta.get(key):
                errors.append(f"missing {key}: {path.relative_to(root)}")
        manifest_targets = list(
            dict.fromkeys(
                target.strip()
                for target in LINK.findall(text)
                if target.strip() in manifest_names
            )
        )
        if source_text_status in {"available", "stale"}:
            if len(manifest_targets) != 1:
                errors.append(f"available source text missing manifest link: {path.relative_to(root)}")
            else:
                target = manifest_targets[0]
                if manifest_sources.get(target) != path.stem:
                    errors.append(f"source-text manifest points to a different source: {path.relative_to(root)} -> {target}")
                manifest_meta = manifest_metadata.get(target, {})
                for key in (
                    "canonical_location",
                    "source_text_location",
                    "source_text_basis",
                    "source_text_hash",
                    "source_text_page_map",
                ):
                    if meta.get(key) != manifest_meta.get(key):
                        errors.append(
                            f"source-text manifest mismatch for {key}: {path.relative_to(root)} -> {target}"
                        )
                field_targets = LINK.findall(meta.get("source_text_manifest", ""))
                if field_targets != [target]:
                    errors.append(f"source_text_manifest field does not match body link: {path.relative_to(root)}")
            if not SOURCE_TEXT_HASH.fullmatch(meta.get("source_text_hash", "")):
                errors.append(f"invalid source_text_hash: {path.relative_to(root)}")
            if not_provided(meta.get("source_text_location", "")):
                errors.append(f"missing available source_text_location: {path.relative_to(root)}")
            if meta.get("source_text_page_map") not in VALID_PAGE_MAPS - {"not provided"}:
                errors.append(f"invalid available source_text_page_map: {path.relative_to(root)}")
        elif source_text_status == "not supplied":
            if manifest_targets:
                errors.append(f"source_text_status not supplied but a manifest link exists: {path.relative_to(root)}")
            for key in ("source_text_location", "source_text_hash", "source_text_page_map", "source_text_manifest"):
                if not_provided(meta.get(key, "")) is False:
                    errors.append(f"source_text_status not supplied but {key} is populated: {path.relative_to(root)}")
        if meta.get("source_text_basis") not in VALID_TEXT_BASES:
            errors.append(
                f"invalid source_text_basis: {path.relative_to(root)} -> "
                f"{meta.get('source_text_basis', '') or 'missing'}"
            )
        if status == "reviewed":
            if not PAGE_ANCHOR.search(text):
                errors.append(f"missing page anchor: {path.relative_to(root)}")
            if not EVIDENCE_LABEL.search(text):
                errors.append(f"missing evidence type label: {path.relative_to(root)}")
        ledger_match = re.search(
            r"^### Evidence ledger\s*\n(.*?)(?=^## |\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if status == "reviewed" and ledger_match:
            bullets = evidence_bullets(ledger_match.group(1))
            if not bullets:
                errors.append(f"empty evidence ledger: {path.relative_to(root)}")
            for index, bullet in enumerate(bullets, start=1):
                lower = bullet.lower()
                if "not supplied" in lower or "not reviewed" in lower:
                    continue
                if not EVIDENCE_LABEL.search(bullet):
                    errors.append(
                        f"evidence ledger item {index} missing evidence type label: "
                        f"{path.relative_to(root)}"
                    )
                if not PAGE_ANCHOR.search(bullet):
                    errors.append(
                        f"evidence ledger item {index} missing page anchor: "
                        f"{path.relative_to(root)}"
                    )

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
        "source_text_manifests": len(manifests),
        "available_source_text": sum(
            1
            for path in references
            if frontmatter(path.read_text(encoding="utf-8")).get("source_text_status") == "available"
        ),
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
