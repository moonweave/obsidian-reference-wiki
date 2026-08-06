#!/usr/bin/env python3
"""Run a standalone first-run smoke test for the Reference release."""
from __future__ import annotations

import json
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
PLACEHOLDER = re.compile(r"\{[a-z_][a-z0-9_]*\}")

VALUES = {
    "preset": "searchable-library",
    "organization": "balanced",
    "source_text_policy": "searchable",
    "source_text_availability": "available",
    "preset_status": "ready",
    "sharing": "private",
    "sync_exposure": "none",
    "next_action": "Create the approved searchable source-text layer and reviewed dossiers.",
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
    "source_text_provenance_version": "not provided",
    "canonical_source_hash": "not provided",
    "canonical_page_count": "not provided",
    "source_text_extractor": "not provided",
    "source_text_extractor_version": "not provided",
    "source_text_extractor_options": "not provided",
    "source_text_extraction_mode": "not provided",
    "source_text_extracted_pages": "not provided",
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
    "full_text_content": "<!-- pdf-page: 1 -->\nA supplied extracted result.\n<!-- formula-not-decoded -->\n<!-- formula-not-decoded -->\n\n<!-- pdf-page: 2 -->\nA supplied limitation.\n<!-- formula-not-decoded -->\n<!-- image -->",
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
    assert (ROOT / "scripts/run_extraction_corpus.py").is_file()
    assert (ROOT / "templates/reference-profile.md").is_file()
    assert (ROOT / "docs/INSTALLATION.md").is_file()
    assert (ROOT / "docs/BETA_TEST.md").is_file()
    onboarding_text = (ROOT / "docs/ONBOARDING.md").read_text(encoding="utf-8")
    for required in (
        "`notes-only`",
        "`searchable-library`",
        "`knowledge-network`",
        "Reference Profile",
        "pending-source-text",
    ):
        assert required in onboarding_text
    assert onboarding_text.index("Start with one plain-language choice") < onboarding_text.index(
        "After the preset choice"
    )
    assert "persisted `Reference Profile`" in skill_text
    payload = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))
    assert payload["skill_name"] == "obsidian-research-wiki-reference"

    corpus = ROOT / "evals/corpus/reference-quality/corpus.json"
    scorer = ROOT / "scripts/score_dossier.py"
    good_score = subprocess.run(
        [
            sys.executable, str(scorer),
            "--corpus", str(corpus),
            "--dossier", str(ROOT / "evals/corpus/reference-quality/candidates/good.md"),
            "--json",
        ],
        check=False, capture_output=True, text=True,
    )
    assert good_score.returncode == 0, good_score.stdout + good_score.stderr
    bad_score = subprocess.run(
        [
            sys.executable, str(scorer),
            "--corpus", str(corpus),
            "--dossier", str(ROOT / "evals/corpus/reference-quality/candidates/unsupported.md"),
            "--json",
        ],
        check=False, capture_output=True, text=True,
    )
    assert bad_score.returncode == 1, bad_score.stdout + bad_score.stderr
    assert json.loads(bad_score.stdout)["unsupported_claims"] >= 1

    preset_cases = (
        (("notes-only", "private", "none", "available"), ("paper-first", "not-applicable", "omit", "available", "ready")),
        (("searchable-library", "private", "none", "available"), ("balanced", "vault-local", "searchable", "available", "ready")),
        (("searchable-library", "private", "public", "available"), ("balanced", "external", "searchable", "available", "ready")),
        (("knowledge-network", "published", "none", "available"), ("concept-network", "external", "searchable", "available", "ready")),
        (("knowledge-network", "private", "none", "none"), ("concept-network", "not supplied", "searchable", "unavailable", "pending-source-text")),
    )
    profile_results: list[dict[str, str]] = []
    for inputs, expected in preset_cases:
        recommended = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/recommend_profile.py"),
                "--preset", inputs[0],
                "--sharing", inputs[1],
                "--sync-exposure", inputs[2],
                "--derived-text", inputs[3],
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert recommended.returncode == 0, recommended.stdout + recommended.stderr
        profile = json.loads(recommended.stdout)
        profile_results.append(profile)
        assert profile["preset"] == inputs[0]
        assert (
            profile["organization"],
            profile["source_text_storage"],
            profile["source_text_policy"],
            profile["source_text_availability"],
            profile["preset_status"],
        ) == expected

    legacy_profile_cases = (
        (("both", "required", "private", "none", "available"), ("balanced", "vault-local")),
        (("both", "required", "private", "public", "available"), ("balanced", "external")),
        (("concept", "required", "published", "none", "available"), ("concept-network", "external")),
        (("paper", "not-required", "private", "none", "none"), ("paper-first", "not supplied")),
    )
    for inputs, expected in legacy_profile_cases:
        recommended = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/recommend_profile.py"),
                "--retrieval", inputs[0],
                "--full-text-search", inputs[1],
                "--sharing", inputs[2],
                "--sync-exposure", inputs[3],
                "--derived-text", inputs[4],
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
        for index, profile in enumerate(profile_results):
            profile_vault = Path(raw) / f"profile-{index}"
            write(
                profile_vault,
                "Reference Index",
                render(
                    ROOT / "templates/reference-index.md",
                    VALUES | {"source_links": "- not provided", "promoted_links": "- not provided"},
                ),
            )
            write(
                profile_vault,
                "Reference Profile",
                render(ROOT / "templates/reference-profile.md", profile),
            )
            profile_checked = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/check_notes.py"),
                    str(profile_vault),
                    "--expect-sources", "0",
                    "--expect-profile",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            assert profile_checked.returncode == 0, profile_checked.stdout + profile_checked.stderr

        extraction_vault = Path(raw) / "extraction-vault"
        extraction_vault.mkdir()
        extraction_output = extraction_vault / "05 Source Text/Full Text/Full Text — Two Page Fixture.md"
        extraction_manifest = extraction_vault / "05 Source Text/Manifests/Source Text — Two Page Fixture.md"
        extracted = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/extract_source_text.py"),
                str(ROOT / "evals/fixtures/source-text/two-page.pdf"),
                "--output", str(extraction_output),
                "--manifest", str(extraction_manifest),
                "--vault-root", str(extraction_vault),
                "--source-name", "Two Page Fixture",
                "--reference-type", "Paper",
                "--storage", "vault-local",
                "--basis", "native-text",
                "--json",
            ],
            check=False, capture_output=True, text=True,
        )
        assert extracted.returncode == 0, extracted.stdout + extracted.stderr
        extraction_result = json.loads(extracted.stdout)
        assert extraction_result["pages"] == 2
        assert extraction_output.read_text(encoding="utf-8").count("<!-- pdf-page:") == 2
        extraction_checked = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_source_text.py"),
                str(extraction_manifest),
                "--vault-root", str(extraction_vault),
                "--json",
            ],
            check=False, capture_output=True, text=True,
        )
        assert extraction_checked.returncode == 0, extraction_checked.stdout + extraction_checked.stderr
        assert json.loads(extraction_checked.stdout)["canonical_page_count"] == 2

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
            "next_action": "Read the supplied source before summarizing it.",
        }
        write(
            vault,
            "Reference Index",
            render(templates / "reference-index.md", VALUES),
        )
        write(
            vault,
            "Reference Profile",
            render(
                templates / "reference-profile.md",
                VALUES | {"source_text_storage": "vault-local"},
            ),
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
                "--expect-profile",
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
        assert result["reference_profiles"] == 1

        unsafe_profile = Path(raw) / "unsafe-profile"
        shutil.copytree(vault, unsafe_profile)
        unsafe_profile_note = unsafe_profile / "Reference Profile.md"
        unsafe_profile_note.write_text(
            unsafe_profile_note.read_text(encoding="utf-8").replace(
                "sync_exposure: none", "sync_exposure: public", 1
            ),
            encoding="utf-8",
        )
        unsafe_profile_checked = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_notes.py"),
                str(unsafe_profile),
                "--expect-sources", "2",
                "--expect-profile",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert unsafe_profile_checked.returncode == 1
        assert "unsafe searchable profile storage" in unsafe_profile_checked.stdout

        semantic_empty = Path(raw) / "semantic-empty"
        shutil.copytree(vault, semantic_empty)
        semantic_source = semantic_empty / "20 Papers/Paper — Anchor Review.md"
        semantic_source.write_text(
            semantic_source.read_text(encoding="utf-8")
            .replace(VALUES["source_summary"], "not supplied")
            .replace(VALUES["source_method"], "not supplied")
            .replace(VALUES["source_measurement"], "not supplied")
            .replace(VALUES["source_theory"], "not supplied")
            .replace(VALUES["source_limitations"], "not supplied")
            .replace(VALUES["review_trace"], "not supplied"),
            encoding="utf-8",
        )
        semantic_checked = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_notes.py"),
                str(semantic_empty),
                "--expect-sources", "2",
                "--json",
            ],
            check=False, capture_output=True, text=True,
        )
        assert semantic_checked.returncode == 1
        assert "source abstract and scope is not supplied" in semantic_checked.stdout

        partial_promotion = Path(raw) / "partial-promotion"
        shutil.copytree(vault, partial_promotion)
        partial_source = partial_promotion / "20 Papers/Paper — Anchor Review.md"
        partial_source.write_text(
            partial_source.read_text(encoding="utf-8").replace(
                "status: reviewed", "status: partial", 1
            ),
            encoding="utf-8",
        )
        partial_checked = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_notes.py"),
                str(partial_promotion),
                "--expect-sources", "2",
                "--json",
            ],
            check=False, capture_output=True, text=True,
        )
        assert partial_checked.returncode == 1
        assert "promoted note references a non-reviewed source" in partial_checked.stdout

        source_text_check = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_source_text.py"),
                str(vault / "05 Source Text/Manifests/Source Text — Anchor Review.md"),
                "--vault-root", str(vault),
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
        assert source_text_result["formula_placeholders"] == 3
        assert source_text_result["formula_placeholder_pages"] == {"1": 2, "2": 1}
        assert source_text_result["image_placeholder_pages"] == {"2": 1}
        escaped_text = Path(raw) / "outside-vault.md"
        escaped_text.write_text("outside\n", encoding="utf-8")
        escaped_values = source_text_values | {
            "source_text_location": "../../../outside-vault.md",
            "source_text_hash": f"sha256:{hashlib.sha256(escaped_text.read_bytes()).hexdigest()}",
            "source_text_page_map": "not provided",
        }
        write(
            vault,
            "05 Source Text/Manifests/Source Text — Escape",
            render(templates / "source-text-manifest.md", escaped_values),
        )
        escaped_check = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_source_text.py"),
                str(vault / "05 Source Text/Manifests/Source Text — Escape.md"),
                "--vault-root", str(vault),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert escaped_check.returncode == 1
        assert "outside the approved Vault root" in escaped_check.stdout
        assert json.loads(escaped_check.stdout)["byte_count"] == 0
        linked_text = vault / "05 Source Text/Full Text/Linked outside.md"
        linked_text.symlink_to(escaped_text)
        linked_values = escaped_values | {
            "source_text_location": "../Full Text/Linked outside.md",
        }
        write(
            vault,
            "05 Source Text/Manifests/Source Text — Symlink Escape",
            render(templates / "source-text-manifest.md", linked_values),
        )
        symlink_check = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_source_text.py"),
                str(vault / "05 Source Text/Manifests/Source Text — Symlink Escape.md"),
                "--vault-root", str(vault),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert symlink_check.returncode == 1
        assert "outside the approved Vault root" in symlink_check.stdout
        assert json.loads(symlink_check.stdout)["byte_count"] == 0
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
                "--vault-root", str(vault),
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
