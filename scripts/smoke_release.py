#!/usr/bin/env python3
"""Run a standalone first-run smoke test for the Reference release."""
from __future__ import annotations

import json
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
PLACEHOLDER = re.compile(r"\{[a-z_][a-z0-9_]*\}")

VALUES = {
    "source_name": "Anchor Review",
    "reference_type": "Paper",
    "source_kind": "paper",
    "source_status": "reviewed",
    "source_text_basis": "native-text",
    "source_text_status": "not supplied",
    "source_text_storage": "not supplied",
    "source_text_location": "not provided",
    "source_text_hash": "not provided",
    "source_text_page_map": "not provided",
    "source_text_manifest": "not provided",
    "reviewed_scope": "PDF pp. 1-2; abstract and results",
    "unreviewed_scope": "references and supplementary material",
    "canonical_location": "/tmp/reference-release-smoke/supplied.pdf",
    "research_problem": "A supplied literature problem.",
    "contribution": "A supplied paper contribution.",
    "system_scope": "A supplied device scope.",
    "source_summary": "A supplied source summary.",
    "source_method": "A supplied paper-specific method.",
    "source_measurement": "A supplied measurement procedure.",
    "source_controls": "A supplied baseline comparison.",
    "source_theory": "A supplied background theory.",
    "source_assumptions": "A supplied model boundary.",
    "source_evidence": "[reported] A supplied result under the stated condition (PDF p. 1, §1).",
    "evidence_ledger": "- [reported] Result under the stated condition: PDF p. 1, §1.",
    "author_interpretation": "A supplied author interpretation.",
    "source_limitations": "A supplied source limitation.",
    "question_relation": "It informs the supplied literature question.",
    "promoted_links": "- Claim: [[Claim — Surface mechanism]]",
    "review_trace": "Native source text reviewed across the named sections; PDF p. 1 checked.",
    "claim_status": "promoted",
    "claim_text": "A supplied claim.",
    "claim_scope": "Applies only under the supplied source conditions.",
    "evidence_link": "not provided",
    "claim_anchor": "PDF p. 1, §1.",
    "claim_alternatives": "No contrary supplied result was reviewed.",
    "limitation_link": "not provided",
    "source_links": "- Paper: [[Paper — Anchor Review]]",
    "capture_reason": "User supplied this source for later review.",
    "next_action": "Read the supplied source before summarizing it.",
    "full_text_content": "<!-- pdf-page: 1 -->\nA supplied extracted result.\n\n<!-- pdf-page: 2 -->\nA supplied limitation.",
}


def render(template: Path, values: dict[str, str]) -> str:
    text = template.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
    assert not PLACEHOLDER.search(text), f"unresolved placeholder in {template.name}"
    return text


def write(vault: Path, name: str, text: str) -> None:
    path = vault / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def assert_links_resolve(vault: Path) -> None:
    names = {path.stem for path in vault.rglob("*.md")}
    for path in vault.rglob("*.md"):
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            assert target.strip() in names, f"{path.name}: missing {target.strip()}"


def main() -> None:
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert re.search(r"^name: obsidian-research-wiki-reference$", skill_text, re.M)
    legacy_names = ("Reference-First " + "Starter", "Research Workspace " + "Advanced")
    assert not any(name in skill_text for name in legacy_names)
    assert (ROOT / "scripts/check_notes.py").is_file()
    payload = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))
    assert payload["skill_name"] == "obsidian-research-wiki-reference"

    profile_cases = (
        (("both", "required", "private", "available"), ("balanced", "vault-local")),
        (("concept", "required", "published", "available"), ("concept-network", "external")),
        (("paper", "not-required", "private", "none"), ("paper-first", "not supplied")),
    )
    for inputs, expected in profile_cases:
        recommended = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/recommend_profile.py"),
                "--retrieval", inputs[0],
                "--full-text-search", inputs[1],
                "--sharing", inputs[2],
                "--derived-text", inputs[3],
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert recommended.returncode == 0, recommended.stdout + recommended.stderr
        profile = json.loads(recommended.stdout)
        assert (profile["organization"], profile["source_text_storage"]) == expected

    with tempfile.TemporaryDirectory(prefix="reference-release-smoke-") as raw:
        vault = Path(raw) / "vault"
        templates = ROOT / "templates"
        write(
            vault,
            "05 Source Text/Full Text/Full Text — Anchor Review",
            render(templates / "full-text.md", VALUES),
        )
        source_text_file = vault / "05 Source Text/Full Text/Full Text — Anchor Review.md"
        source_text_values = VALUES | {
            "source_text_status": "available",
            "source_text_storage": "vault-local",
            "source_text_location": "../Full Text/Full Text — Anchor Review.md",
            "source_text_hash": f"sha256:{hashlib.sha256(source_text_file.read_bytes()).hexdigest()}",
            "source_text_page_map": "pdf-page-comments",
            "source_text_manifest": "[[Source Text — Anchor Review]]",
        }
        capture_values = VALUES | {
            "source_status": "not reviewed",
            "source_text_status": "not reviewed",
            "source_text_storage": "not reviewed",
            "source_text_location": "not provided",
            "source_text_hash": "not provided",
            "source_text_page_map": "not provided",
            "source_text_manifest": "not provided",
        }
        write(
            vault,
            "Reference Index",
            render(templates / "reference-index.md", VALUES),
        )
        write(
            vault,
            "20 Papers/Paper — Anchor Review",
            render(templates / "source.md", source_text_values),
        )
        write(
            vault,
            "05 Source Text/Manifests/Source Text — Anchor Review",
            render(templates / "source-text-manifest.md", source_text_values),
        )
        write(
            vault,
            "20 Claims/Claim — Surface mechanism",
            render(templates / "claim.md", VALUES),
        )
        write(
            vault,
            "10 Sources/Source — Unread item",
            render(templates / "source-capture.md", capture_values),
        )
        write(vault, "Reading Queue", "## Reading Queue\n")
        assert_links_resolve(vault)
        assert not any(
            path.name.startswith(("Experiment", "Observation"))
            for path in vault.rglob("*.md")
        )

        checked = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_notes.py"),
                str(vault),
                "--expect-sources",
                "2",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert checked.returncode == 0, checked.stdout + checked.stderr
        result = json.loads(checked.stdout)
        assert result["status"] == "pass"
        assert result["sources"] == 2
        assert result["reviewed_sources"] == 1
        assert result["capture_sources"] == 1
        assert result["promoted_notes"] == 1
        assert result["source_text_manifests"] == 1
        assert result["available_source_text"] == 1

        source_text_check = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_source_text.py"),
                str(vault / "05 Source Text/Manifests/Source Text — Anchor Review.md"),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert source_text_check.returncode == 0, source_text_check.stdout + source_text_check.stderr
        source_text_result = json.loads(source_text_check.stdout)
        assert source_text_result["status"] == "pass"
        assert source_text_result["page_markers"] == 2
        mismatched_source = vault / "20 Papers/Paper — Anchor Review.md"
        mismatched_source.write_text(
            mismatched_source.read_text(encoding="utf-8").replace(
                source_text_values["source_text_hash"], "sha256:" + "0" * 64, 1
            ),
            encoding="utf-8",
        )
        mismatch_check = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_notes.py"),
                str(vault),
                "--expect-sources",
                "2",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert mismatch_check.returncode == 1
        assert "source-text manifest mismatch for source_text_hash" in mismatch_check.stdout
        mismatched_source.write_text(
            mismatched_source.read_text(encoding="utf-8").replace(
                "sha256:" + "0" * 64, source_text_values["source_text_hash"], 1
            ),
            encoding="utf-8",
        )
        source_text_file.write_text(source_text_file.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
        tampered_source_text = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_source_text.py"),
                str(vault / "05 Source Text/Manifests/Source Text — Anchor Review.md"),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert tampered_source_text.returncode == 1
        assert "source_text_hash mismatch" in tampered_source_text.stdout

    print("PASS: standalone Reference release first-run smoke")


if __name__ == "__main__":
    main()
