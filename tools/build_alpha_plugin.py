"""Build the independent alpha plugin as a deterministic root-level ZIP."""
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
PACKAGE = ROOT / "plugins" / "cloudcodex-windows-bootstrap-alpha"
SKIP_PARTS = {"__pycache__", ".pytest_cache", ".git"}


def package_files(package: Path = PACKAGE) -> list[Path]:
    """Return sorted regular files suitable for the portable alpha archive."""
    result: list[Path] = []
    for path in sorted(package.rglob("*"), key=lambda item: item.relative_to(package).as_posix()):
        relative = path.relative_to(package)
        if SKIP_PARTS.intersection(relative.parts) or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise ValueError(f"Symlinks are not distributable: {relative}")
        if not path.is_file():
            continue
        if path.name == ".env" or path.suffix in {".key", ".pem", ".pfx"}:
            raise ValueError(f"Unexpected credential-like file: {relative}")
        result.append(path)
    if not result:
        raise ValueError("Alpha package directory is empty.")
    return result


def archive_bytes(package: Path, destination: Path) -> str:
    """Write a reproducible, single-root archive and return its SHA-256."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".tmp", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_STORED) as archive:
            for path in package_files(package):
                entry = zipfile.ZipInfo(path.relative_to(package).as_posix(), (1980, 1, 1, 0, 0, 0))
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                entry.compress_type = zipfile.ZIP_STORED
                archive.writestr(entry, path.read_bytes())
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError("Alpha archive failed CRC verification.")
        digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
        temporary.replace(destination)
        return digest
    finally:
        if temporary.exists():
            temporary.unlink()


def source_revision() -> str:
    """Return source provenance without requiring network access."""
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], check=True,
            capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "not_observed"


def build(output: Path | None = None) -> dict[str, object]:
    """Build the alpha archive without publishing or contacting a provider."""
    manifest = json.loads((PACKAGE / "plugin.json").read_text(encoding="utf-8"))
    name, version = manifest["name"], manifest["version"]
    if name != "cloudcodex-windows-bootstrap-alpha" or not re.fullmatch(
        r"\d+\.\d+\.\d+-alpha\.\d+", version
    ):
        raise ValueError("Unexpected alpha package identity or version.")
    output = output or ROOT / "dist-alpha"
    archive_name = f"{name}-{version}.zip"
    digest = archive_bytes(PACKAGE, output / archive_name)
    report = {
        "plugin": name, "version": version, "archive": archive_name,
        "sha256": digest, "source_revision": source_revision(),
        "file_count": len(package_files()),
        "format": "single plugin at archive root; ZIP_STORED; fixed metadata",
    }
    (output / "SHA256SUMS").write_text(f"{digest}  {archive_name}\n", encoding="utf-8", newline="\n")
    (output / "release-manifest.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.output), indent=2))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
