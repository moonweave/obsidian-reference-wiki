#!/usr/bin/env python3
"""Recommend Reference organization and source-text storage from onboarding answers."""
from __future__ import annotations

import argparse
import json


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retrieval", choices=("paper", "concept", "both"), required=True)
    parser.add_argument(
        "--full-text-search",
        choices=("required", "not-required"),
        required=True,
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
        print(f"Recommended configuration: {result['organization']} + {result['source_text_storage']}")
        print(f"Organization: {result['organization_reason']}")
        print(f"Storage: {result['storage_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
