#!/usr/bin/env python3
"""Recommend a Reference onboarding preset and its safe storage profile."""
from __future__ import annotations

import argparse
import json


PRESET_DEFAULTS = {
    "notes-only": ("paper-first", "not-required"),
    "searchable-library": ("balanced", "required"),
    "knowledge-network": ("concept-network", "required"),
}

PRESET_REASONS = {
    "notes-only": "Create reviewed Paper/Source dossiers without creating or importing a full-text derivative.",
    "searchable-library": "Keep reviewed dossiers and make authorized full text searchable for later verification.",
    "knowledge-network": "Keep searchable full text and dossiers, then promote reusable cross-paper knowledge selectively.",
}


def recommend(
    retrieval: str,
    full_text_search: str,
    sharing: str,
    sync_exposure: str,
    derived_text: str,
) -> dict[str, str]:
    organization = {
        "paper": "paper-first",
        "concept": "concept-network",
        "both": "balanced",
    }[retrieval]

    if derived_text == "none":
        storage = "not supplied"
        storage_reason = "No authorized parsed/OCR derivative is available; create no empty cache."
    elif sharing in {"shared", "published"} or sync_exposure in {"public", "uncertain"}:
        storage = "external"
        storage_reason = "A shared, published, publicly synchronized, or uncertain Vault should keep the full derivative outside its sharing boundary."
    elif full_text_search == "required":
        storage = "vault-local"
        storage_reason = "A private Vault with full-text search benefits from a local regenerable Markdown cache."
    else:
        storage = "external"
        storage_reason = "Full-text Vault search is not required, so external storage avoids unnecessary cache exposure."

    organization_reason = {
        "paper-first": "Individual paper recall is primary; promote reusable concepts selectively.",
        "balanced": "Paper recall and cross-paper synthesis both matter; keep rich dossiers and selective promoted notes.",
        "concept-network": "Cross-paper concept retrieval is primary; retain every Paper/Source dossier as provenance.",
    }[organization]

    return {
        "organization": organization,
        "source_text_storage": storage,
        "organization_reason": organization_reason,
        "storage_reason": storage_reason,
    }


def recommend_preset(
    preset: str,
    sharing: str,
    sync_exposure: str,
    derived_text: str,
) -> dict[str, str]:
    organization, full_text_search = PRESET_DEFAULTS[preset]
    source_text_policy = "omit" if preset == "notes-only" else "searchable"
    source_text_availability = "available" if derived_text == "available" else "unavailable"
    retrieval = {
        "paper-first": "paper",
        "balanced": "both",
        "concept-network": "concept",
    }[organization]
    result = recommend(
        retrieval,
        full_text_search,
        sharing,
        sync_exposure,
        derived_text,
    )
    if preset == "notes-only":
        result["source_text_storage"] = "not-applicable"
        result["storage_reason"] = (
            "The notes-only preset does not create or import a full-text derivative. "
            "Preserve any existing derivative in place unless it is separately authorized."
        )
        preset_status = "ready"
        next_action = "Create reviewed Paper/Source dossiers; preserve any existing derivative in place."
    elif source_text_availability == "unavailable":
        preset_status = "pending-source-text"
        next_action = "Supply or authorize a derivative before claiming full-text search is ready."
    else:
        preset_status = "ready"
        next_action = "Create the approved searchable source-text layer and reviewed dossiers."
    return {
        "preset": preset,
        "preset_reason": PRESET_REASONS[preset],
        "source_text_policy": source_text_policy,
        "source_text_availability": source_text_availability,
        "preset_status": preset_status,
        "sharing": sharing,
        "sync_exposure": sync_exposure,
        "next_action": next_action,
        **result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=tuple(PRESET_DEFAULTS))
    parser.add_argument("--retrieval", choices=("paper", "concept", "both"))
    parser.add_argument(
        "--full-text-search",
        choices=("required", "not-required"),
    )
    parser.add_argument("--sharing", choices=("private", "shared", "published"), required=True)
    parser.add_argument(
        "--sync-exposure",
        choices=("none", "controlled", "public", "uncertain"),
        required=True,
    )
    parser.add_argument("--derived-text", choices=("available", "none"), required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    if args.preset and (args.retrieval or args.full_text_search):
        parser.error("--preset cannot be combined with legacy retrieval arguments")
    if args.preset:
        result = recommend_preset(
            args.preset,
            args.sharing,
            args.sync_exposure,
            args.derived_text,
        )
    else:
        if not args.retrieval or not args.full_text_search:
            parser.error("use --preset, or provide both --retrieval and --full-text-search")
        result = recommend(
            args.retrieval,
            args.full_text_search,
            args.sharing,
            args.sync_exposure,
            args.derived_text,
        )
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if "preset" in result:
            print(f"Preset: {result['preset']}")
            print(f"Depth: {result['preset_reason']}")
            print(
                "Source text: "
                f"{result['source_text_policy']} + {result['source_text_availability']}"
            )
            print(f"Preset status: {result['preset_status']}")
            print(f"Next action: {result['next_action']}")
        print(f"Recommended configuration: {result['organization']} + {result['source_text_storage']}")
        print(f"Organization: {result['organization_reason']}")
        print(f"Storage: {result['storage_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
