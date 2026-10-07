"""Check or update strategy-local copies of the canonical bootstrap resources."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'skills/github-actions-windows-bootstrap/references'
STRATEGIES = ('windows-ci-ephemeral-branch','windows-ci-managed-branch','windows-ci-fork-fallback')
MAP = {
    'execution-contract.md': 'execution-contract.md',
    'github-access.md': 'github-access.md',
    'github-constraints.md': 'github-constraints.md',
    'ephemeral-workflow.yml.template': 'windows-workflow.yml.template',
}


def synchronize(write: bool = False) -> list[str]:
    """Return out-of-sync paths and optionally refresh them from the canonical source."""
    mismatches: list[str] = []
    for skill in STRATEGIES:
        dest_root = ROOT / 'skills' / skill / 'references'
        # Each strategy is self-contained at runtime, so shared references are copied here.
        for src_name, dest_name in MAP.items():
            src = ENTRY / src_name
            dest = dest_root / dest_name
            if not dest.exists() or dest.read_bytes() != src.read_bytes():
                mismatches.append(dest.relative_to(ROOT).as_posix())
                if write:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dest)
    return mismatches


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    bad = synchronize(args.write)
    if bad and not args.write:
        raise SystemExit('Out of sync:\n' + '\n'.join(bad))
    print('strategy references synchronized' if args.write else 'strategy references in sync')
