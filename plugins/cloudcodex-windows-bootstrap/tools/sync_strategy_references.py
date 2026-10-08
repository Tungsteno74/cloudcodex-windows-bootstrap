"""Check or update bundled strategy contracts and YAML assets."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "skills/github-actions-windows-bootstrap"
STRATEGIES = (
    "windows-ci-ephemeral-branch",
    "windows-ci-managed-branch",
    "windows-ci-fork-fallback",
)
REFERENCE_FILES = (
    "execution-contract.md",
    "github-access.md",
    "github-constraints.md",
)
ASSET_FILES = ("windows-workflow.yml",)


def synchronize(write: bool = False) -> list[str]:
    """Return unsynchronized file paths, writing copies only if requested."""
    mismatches: list[str] = []
    for strategy in STRATEGIES:
        skill_root = ROOT / "skills" / strategy
        for directory, filenames in (
            ("references", REFERENCE_FILES),
            ("assets", ASSET_FILES),
        ):
            for name in filenames:
                source = ENTRY / directory / name
                destination = skill_root / directory / name
                if destination.is_file() and destination.read_bytes() == source.read_bytes():
                    continue
                mismatches.append(destination.relative_to(ROOT).as_posix())
                if write:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, destination)
    return mismatches


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    divergent = synchronize(arguments.write)
    if divergent and not arguments.write:
        raise SystemExit("Out of sync: " + ", ".join(divergent))
    print("strategy resources synchronized" if arguments.write
          else "strategy resources in sync")
