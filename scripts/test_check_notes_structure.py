import tempfile
import unittest
from pathlib import Path
from check_notes import check


class Structure(unittest.TestCase):
    def test_examples_math_and_template_are_not_unfinished_notes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "templates").mkdir()
            (root / "templates/concept.md").write_text("# {{title}}\n[[{target}]]")
            (root / "Guide.md").write_text("## Examples\n`[[filename]]`\n```markdown\n# Guide\n[[missing]] {title}\n```\nGamma ${_gamma}$ and $\\mathrm{polymer}$.")
            self.assertEqual(check(root)["errors"], [])
            (root / "Guide.md").write_text("## Body\nUnfinished {title}\n[[missing]]")
            errors = check(root)["errors"]
            self.assertTrue(any("unresolved template placeholder" in e for e in errors))
            self.assertTrue(any("unresolved wikilink" in e for e in errors))

    def test_legacy_duplicates_are_visible_but_ambiguous_links_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for folder in ["research", "dispatch/a", "dispatch/b"]:
                (root / folder).mkdir(parents=True)
            for folder in ["dispatch/a", "dispatch/b"]:
                (root / folder / "draft.md").write_text("## Body")
            (root / "Reader.md").write_text("[[dispatch/a/draft]] [[dispatch/b/draft]]")
            result = check(root, library_scope="research")
            self.assertEqual(result["errors"], [])
            self.assertEqual(len(result["warnings"]), 1)
            self.assertTrue(any("duplicate Markdown basename" in e for e in check(root)["errors"]))
            (root / "Reader.md").write_text("[[draft]]")
            self.assertTrue(any("ambiguous wikilink" in e for e in check(root, library_scope="research")["errors"]))
            (root / "dispatch/a/draft.md").write_text("---\ntype: reference-record\n---\n")
            self.assertTrue(any("duplicate Markdown basename" in e for e in check(root, library_scope="research")["errors"]))


if __name__ == "__main__":
    unittest.main()
