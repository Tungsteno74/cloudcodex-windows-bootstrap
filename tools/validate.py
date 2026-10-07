"""Run all package and distribution checks; no repository/provider mutations."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from build_release import build

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'plugins/cloudcodex-windows-bootstrap'


def run(arguments: list[str]) -> None:
    """Run one validation command with stable UTF-8 and no bytecode side effects."""
    environment = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    subprocess.run([sys.executable, '-X', 'utf8', *arguments], cwd=ROOT,
                   env=environment, check=True)


def main() -> int:
    try:
        # Strategy bundles must match their canonical bootstrap references before tests run.
        run([str(PACKAGE / 'tools/sync_strategy_references.py')])
        run(['-m', 'unittest', 'discover', '-s', str(PACKAGE / 'tests'), '-v'])
        run(['-m', 'unittest', 'discover', '-s', 'tests', '-v'])
        # Two independent builds catch accidental timestamp/order drift before publishing.
        with tempfile.TemporaryDirectory(prefix='plugin-build-check-') as temporary:
            first = build(ROOT, Path(temporary) / 'first')
            second = build(ROOT, Path(temporary) / 'second')
            if first['sha256'] != second['sha256']:
                raise ValueError('Two builds produced different archive bytes.')
        report = build(ROOT)
        print(json.dumps({'validation': 'passed', 'package': report}, indent=2))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Validation failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
