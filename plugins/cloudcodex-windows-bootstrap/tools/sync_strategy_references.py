"""Check or update local strategy resources and embedded workflow templates."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "skills/github-actions-windows-bootstrap/references"
STRATEGIES = (
    "windows-ci-ephemeral-branch",
    "windows-ci-managed-branch",
    "windows-ci-fork-fallback",
)
MAP = {
    "execution-contract.md": "execution-contract.md",
    "github-access.md": "github-access.md",
    "github-constraints.md": "github-constraints.md",
    "ephemeral-workflow.yml.template": "windows-workflow.yml.template",
}
INLINE_START = "<!-- BEGIN SYNCED WINDOWS WORKFLOW TEMPLATE -->"
INLINE_END = "<!-- END SYNCED WINDOWS WORKFLOW TEMPLATE -->"


def embedded_block(template: str) -> str:
    """Render the exact canonical template inside a skill's loaded instructions."""
    fence = chr(96) * 3
    return (f"{INLINE_START}\n{fence}yaml\n{template.rstrip()}\n"
            f"{fence}\n{INLINE_END}")


def synchronize(write: bool = False) -> list[str]:
    """Return divergent local files, optionally updating them deterministically."""
    mismatches: list[str] = []
    template = (ENTRY / "ephemeral-workflow.yml.template").read_text(encoding="utf-8")
    expected = embedded_block(template)

    for skill in STRATEGIES:
        skill_root = ROOT / "skills" / skill
        resources = skill_root / "references"
        for source_name, destination_name in MAP.items():
            source = ENTRY / source_name
            destination = resources / destination_name
            if not destination.is_file() or destination.read_bytes() != source.read_bytes():
                mismatches.append(destination.relative_to(ROOT).as_posix())
                if write:
                    resources.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, destination)

        instruction_path = skill_root / "SKILL.md"
        text = instruction_path.read_text(encoding="utf-8")
        if text.count(INLINE_START) != 1 or text.count(INLINE_END) != 1:
            raise ValueError(f"Missing or duplicate inline markers: {instruction_path}")
        before, rest = text.split(INLINE_START, 1)
        _, after = rest.split(INLINE_END, 1)
        updated = before + expected + after
        if updated != text:
            mismatches.append(instruction_path.relative_to(ROOT).as_posix())
            if write:
                with instruction_path.open("w", encoding="utf-8", newline="\n") as stream:
                    stream.write(updated)
    return mismatches


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    divergent = synchronize(args.write)
    if divergent and not args.write:
        raise SystemExit("Out of sync:\n" + "\n".join(divergent))
    print("strategy resources synchronized" if args.write else "strategy resources in sync")
