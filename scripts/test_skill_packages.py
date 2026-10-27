import tempfile
import unittest
from pathlib import Path

from build_skill_packages import build, NAMES, ROOT


class SkillPackages(unittest.TestCase):
    def test_both_names_are_self_contained_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as raw:
            packages = build(Path(raw))
            for name, path in zip(NAMES, packages):
                self.assertIn(f"name: {name}\n", (path / "SKILL.md").read_text())
                for resource in ("docs/CONTRACT.md", "templates/source.md",
                                 "scripts/check_notes.py", "evals/evals.json"):
                    self.assertEqual((ROOT / resource).read_bytes(), (path / resource).read_bytes())
                self.assertFalse(any(p.is_symlink() for p in path.rglob("*")))
            before = (packages[1] / "SKILL.md").read_bytes()
            with self.assertRaises(FileExistsError):
                build(Path(raw))
            self.assertEqual((packages[1] / "SKILL.md").read_bytes(), before)

    def test_source_checkout_cannot_be_package_output(self):
        with self.assertRaises(ValueError):
            build(ROOT / "packages")


if __name__ == "__main__":
    unittest.main()
