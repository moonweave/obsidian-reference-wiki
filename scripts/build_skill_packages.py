#!/usr/bin/env python3
"""Build standalone canonical and legacy-name skills without touching installs."""
import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("obsidian-reference-wiki", "obsidian-research-wiki-reference")
FILES = ("SKILL.md", "README.md", "README.ko.md", "LICENSE", "NOTICE",
         "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md", "docs", "templates", "scripts", "evals")


def build(output: Path) -> list[Path]:
    output = output.expanduser().resolve()
    if output == ROOT or output.is_relative_to(ROOT):
        raise ValueError("package output must be outside the source checkout")
    targets = [output / name for name in NAMES]
    if any(path.exists() for path in targets):
        raise FileExistsError("refusing to overwrite an existing skill package")
    for name, target in zip(NAMES, targets):
        target.mkdir(parents=True)
        for entry in FILES:
            source = ROOT / entry
            if source.is_dir():
                shutil.copytree(source, target / entry,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            else:
                shutil.copy2(source, target / entry)
        skill = target / "SKILL.md"
        skill.write_text(re.sub(r"(?m)^name: (?:obsidian-reference-wiki|obsidian-research-wiki-reference)$",
                               f"name: {name}", skill.read_text(), count=1))
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        paths = build(args.output)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
