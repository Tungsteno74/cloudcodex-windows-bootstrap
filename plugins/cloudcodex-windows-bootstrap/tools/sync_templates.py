"""Keep distributed strategy templates in sync; authoring only, no network I/O."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

STRATEGIES = (
    "windows-ci-ephemeral-branch",
    "windows-ci-managed-branch",
    "windows-ci-fork-fallback",
)


def synchronize(root: Path, *, write: bool = False) -> list[str]:
    """Return divergent relative paths; write only with an explicit caller choice."""
    # The bootstrap template is the authoring source; strategies ship local runtime copies.
    source = root / "skills/github-actions-windows-bootstrap/references/ephemeral-workflow.yml.template"
    content = source.read_bytes()
    divergent: list[str] = []
    for strategy in STRATEGIES:
        target = root / "skills" / strategy / "references/windows-workflow.yml.template"
        if target.exists() and target.read_bytes() == content:
            continue
        divergent.append(target.relative_to(root).as_posix())
        if write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    return divergent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Update distributed copies.")
    args = parser.parse_args()
    try:
        differences = synchronize(Path(__file__).resolve().parents[1], write=args.write)
    except OSError as error:
        print(f"Template synchronization failed: {error}", file=sys.stderr)
        return 2
    if differences:
        print(("Updated" if args.write else "Divergent") + ": " + ", ".join(differences))
        return 0 if args.write else 1
    print("Strategy templates match the authoring source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
