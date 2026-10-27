import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_notes import check
from smoke_release import ROOT, VALUES, render


class ReferenceContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {"REFERENCE_SCHEMA_MODE": "current"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def write(self, name, text):
        path = self.root / (name + ".md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def source(self, status="reviewed", kind="paper", anchor="PDF p. 1"):
        values = {**VALUES, "review_status": status, "reference_kind": kind,
                  "promoted_links": "not provided"}
        text = render(ROOT / "templates/source.md", values)
        text = text.replace("PDF p. 1", anchor).replace("PDF pp. 1-2", anchor)
        return self.write("10 Sources/Paper — Anchor Review", text)

    def claim(self, target, anchor=""):
        return self.write("20 Claims/Claim — Test", "---\ntype: reference-claim\n"
                          "grounding_status: source-grounded\n---\n## Evidence\n"
                          f"- Paper: [[{target}]]\n{anchor}\n")

    def errors(self):
        return check(self.root, expected_sources=1)["errors"]

    def test_unreviewed_sources_rejected_for_all_link_forms(self):
        source = self.source(status="partial")
        source.write_text(source.read_text().replace("type: reference-record", "type: reference-record\naliases: [Pilot]"))
        for target in ("Paper — Anchor Review", "10 Sources/Paper — Anchor Review",
                       "../10 Sources/Paper — Anchor Review.md", "Pilot"):
            with self.subTest(target=target):
                self.claim(target, "PDF p. 1")
                self.assertTrue(any("non-reviewed source" in e for e in self.errors()))

    def test_reviewed_path_and_alias_require_anchor(self):
        source = self.source()
        source.write_text(source.read_text().replace("type: reference-record", "type: reference-record\naliases: [Pilot]"))
        for target in ("10 Sources/Paper — Anchor Review", "../10 Sources/Paper — Anchor Review.md", "Pilot"):
            with self.subTest(target=target):
                self.claim(target)
                self.assertTrue(any("anchor" in e for e in self.errors()))
                self.claim(target, "PDF p. 1")
                self.assertEqual(self.errors(), [])

    def test_source_kind_locators(self):
        for kind, anchor in (("web-page", "Section: Results, paragraph 2"),
                             ("standard", "Clause: 4.2"),
                             ("dataset", "Version: v2, row: 42, column: yield")):
            with self.subTest(kind=kind):
                source = self.source(kind=kind, anchor=anchor)
                for value in (VALUES["source_method"], VALUES["source_measurement"],
                              VALUES["source_controls"], VALUES["source_theory"]):
                    source.write_text(source.read_text().replace(value, "not applicable"))
                self.assertEqual(self.errors(), [])
                source.write_text(source.read_text().replace(anchor, "no locator")
                                  .replace("§1", "unlocated").replace("§2", "unlocated"))
                self.assertTrue(any("anchor" in e for e in self.errors()))

    def test_paper_still_needs_pdf_anchor(self):
        self.source(anchor="Section: Results")
        self.assertTrue(any("anchor" in e for e in self.errors()))

    def test_open_question_can_link_unread_but_answer_cannot(self):
        self.source(status="partial")
        q = self.write("60 Questions/Question — Test", "---\ntype: reference-question\n"
                       "question_status: open\n---\nWhat should we test?\n"
                       "- Reference to review: [[10 Sources/Paper — Anchor Review]]\n")
        self.assertEqual(self.errors(), [])
        q.write_text(q.read_text().replace("question_status: open", "question_status: answered")
                     + "\n## Answer\n[reported] A result. PDF p. 1\n")
        self.assertTrue(any("non-reviewed source" in e for e in self.errors()))

    def test_claim_cannot_avoid_source_with_heading_only(self):
        self.source()
        self.write("20 Claims/Claim — Test", "---\ntype: reference-claim\n"
                   "grounding_status: source-grounded\n---\n## Source anchor\nPDF p. 1\n")
        self.assertTrue(any("source provenance" in e for e in self.errors()))

    def test_open_question_template_needs_no_invented_candidate(self):
        self.source()
        values = {**VALUES, "reading_candidates": "not provided", "question_anchor": "not provided"}
        self.write("60 Questions/Question — New question", render(ROOT / "templates/question.md", values))
        self.assertEqual(self.errors(), [])

    def test_legacy_library_filename_provenance(self):
        source = self.source()
        text = source.read_text().replace("type: reference-record", "type: reference-record\nsummary_basis: sections")
        # This is an isolated fixture rename, never a migration of user notes.
        legacy = source.with_name("author2023.md")
        source.rename(legacy)
        legacy.write_text(text)
        self.claim("10 Sources/author2023", "PDF p. 1")
        self.assertEqual(check(self.root, expected_sources=1, library_scope="10 Sources")["errors"], [])
        legacy.write_text(text.replace("review_status: reviewed", "review_status: partial"))
        self.assertTrue(any("non-reviewed source" in e for e in
                            check(self.root, expected_sources=1, library_scope="10 Sources")["errors"]))


if __name__ == "__main__":
    unittest.main()
