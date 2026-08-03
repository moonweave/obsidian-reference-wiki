#!/usr/bin/env python3
"""Run a standalone first-run smoke test for the Reference release."""
from __future__ import annotations

import json
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

    with tempfile.TemporaryDirectory(prefix="reference-release-smoke-") as raw:
        vault = Path(raw) / "vault"
        templates = ROOT / "templates"
        write(
            vault,
            "Reference Index",
            render(templates / "reference-index.md", VALUES),
        )
        write(
            vault,
            "20 Papers/Paper — Anchor Review",
            render(templates / "source.md", VALUES),
        )
        write(
            vault,
            "20 Claims/Claim — Surface mechanism",
            render(templates / "claim.md", VALUES),
        )
        write(
            vault,
            "10 Sources/Source — Unread item",
            render(templates / "source-capture.md", VALUES),
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

    print("PASS: standalone Reference release first-run smoke")


if __name__ == "__main__":
    main()
