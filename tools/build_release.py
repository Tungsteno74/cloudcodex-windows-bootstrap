"""Build a single-plugin archive with deterministic bytes and provenance metadata."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'plugins/cloudcodex-windows-bootstrap'
SKIP_PARTS = {'__pycache__', '.pytest_cache', '.git'}


def package_files(package: Path) -> list[Path]:
    """Return regular source files, refusing links and accidental credentials."""
    result: list[Path] = []
    # Archive order is part of the reproducibility contract, so sort by portable path.
    for path in sorted(package.rglob('*'), key=lambda item: item.relative_to(package).as_posix()):
        relative = path.relative_to(package)
        if SKIP_PARTS.intersection(relative.parts) or path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.is_symlink():
            raise ValueError('Symlinks are not distributable: ' + str(relative))
        if not path.is_file():
            continue
        if path.name == '.env' or path.suffix in {'.key', '.pem', '.pfx'}:
            raise ValueError('Unexpected credential-like file: ' + str(relative))
        result.append(path)
    if not result:
        raise ValueError('Plugin directory is empty.')
    return result


def archive_bytes(package: Path, destination: Path) -> str:
    """Use stable entry metadata and ZIP_STORED for cross-platform reproducibility."""
    files = package_files(package)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.tmp', delete=False) as temp:
        temporary = Path(temp.name)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_STORED) as archive:
            for path in files:
                name = path.relative_to(package).as_posix()
                # Normalize timestamp and permissions so Linux and Windows emit identical bytes.
                entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                entry.compress_type = zipfile.ZIP_STORED
                archive.writestr(entry, path.read_bytes())
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError('Archive failed its CRC verification.')
        digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
        temporary.replace(destination)
        return digest
    finally:
        if temporary.exists():
            temporary.unlink()


def source_revision(root: Path) -> str:
    """Return the source commit for release provenance when Git is available."""
    try:
        result = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return 'not_observed'


def build(root: Path = ROOT, output: Path | None = None) -> dict:
    """Build the archive and checksums; no network or provider writes."""
    package = root / 'plugins/cloudcodex-windows-bootstrap'
    manifest = json.loads((package / 'plugin.json').read_text(encoding='utf-8'))
    name, version = manifest['name'], manifest['version']
    if name != 'cloudcodex-windows-bootstrap' or not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Unexpected package identity or release version.')
    output = output or root / 'dist'
    archive_name = f'{name}-{version}.zip'
    digest = archive_bytes(package, output / archive_name)
    # The manifest lets release automation verify artifact identity without rebuilding it.
    report = {
        'plugin': name, 'version': version,
        'archive': archive_name, 'sha256': digest,
        'source_revision': source_revision(root),
        'file_count': len(package_files(package)),
        'format': 'single plugin at archive root; ZIP_STORED; fixed metadata',
    }
    for filename, content in (
        ('SHA256SUMS', f'{digest}  {archive_name}\n'),
        ('release-manifest.json', json.dumps(report, indent=2) + '\n'),
    ):
        with (output / filename).open('w', encoding='utf-8', newline='\n') as stream:
            stream.write(content)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(build(output=args.output), indent=2))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
