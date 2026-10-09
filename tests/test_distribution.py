"""Repository-level regressions; these do not execute an LLM or consumer CI."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'plugins/cloudcodex-windows-bootstrap'
sys.path.insert(0, str(ROOT / 'tools'))
from build_release import archive_bytes, build, package_files  # noqa: E402


class DistributionTests(unittest.TestCase):
    def test_repository_is_standalone_plugin_source(self) -> None:
        self.assertFalse((ROOT / '.agents/plugins/marketplace.json').exists())
        self.assertEqual(PACKAGE.name, 'cloudcodex-windows-bootstrap')
        manifest = json.loads((PACKAGE / 'plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['name'], PACKAGE.name)

    def test_author_and_version_consistent(self) -> None:
        native = json.loads((PACKAGE / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        portable = json.loads((PACKAGE / 'plugin.json').read_text(encoding='utf-8'))
        for manifest in (native, portable):
            self.assertEqual(manifest['author']['name'], 'Tungsteno74')
            self.assertEqual(manifest['version'], '0.6.6')
        self.assertEqual(native['interface'], portable['extensions']['com.openai']['interface'])
        self.assertEqual(native['interface']['developerName'], 'Tungsteno74')

    def test_license_in_repository_and_package(self) -> None:
        text = (ROOT / 'LICENSE').read_bytes()
        self.assertEqual(text, (PACKAGE / 'LICENSE').read_bytes())
        self.assertIn(b'MIT License', text)
        self.assertIn(b'2026 Tungsteno74', text)

    def test_five_skill_bundles_and_frontmatter(self) -> None:
        paths = sorted((PACKAGE / 'skills').glob('*/SKILL.md'))
        self.assertEqual(len(paths), 5)
        for path in paths:
            text = path.read_text(encoding='utf-8')
            self.assertTrue(text.startswith('---\n'))
            metadata = yaml.safe_load(text.split('---', 2)[1])
            self.assertEqual(metadata['name'], path.parent.name)
            self.assertTrue(metadata['description'])

    def test_probe_fingerprints_match_expected_baseline(self) -> None:
        records = json.loads((PACKAGE / 'tests/probe-fingerprints.json').read_text(encoding='utf-8'))
        for path, digest in records.items():
            self.assertEqual(hashlib.sha256((PACKAGE / path).read_bytes()).hexdigest(), digest)

    def test_package_markdown_links_resolve_locally(self) -> None:
        for path in PACKAGE.rglob('*.md'):
            text = path.read_text(encoding='utf-8')
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#'):
                    continue
                target_path = (path.parent / target.split('#', 1)[0]).resolve()
                self.assertTrue(target_path.is_file(), str(path) + ': ' + target)
                self.assertTrue(target_path == PACKAGE.resolve() or PACKAGE.resolve() in target_path.parents)

    def test_no_credentials_or_local_paths_in_distributable(self) -> None:
        for path in package_files(PACKAGE):
            text = path.read_bytes().decode('utf-8', errors='ignore')
            # Public packages must not leak account-plugin IDs, local paths, or token-shaped values.
            self.assertIsNone(re.search(r'\bPlugin_[0-9a-f]{16,}\b', text), str(path))
            self.assertIsNone(re.search(r'[A-Za-z]:\\Users\\', text), str(path))
            self.assertIsNone(re.search(r'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}', text), str(path))

    def test_canonical_workflow_assets_have_supported_extension(self) -> None:
        template = PACKAGE / 'skills/github-actions-windows-bootstrap/assets/windows-workflow.yml'
        self.assertTrue(template.is_file())
        for directory in (PACKAGE / 'skills').iterdir():
            if not directory.is_dir():
                continue
            self.assertFalse(list(directory.rglob('*.template')))
        for strategy in ('windows-ci-managed-branch', 'windows-ci-ephemeral-branch',
                         'windows-ci-fork-fallback'):
            target = PACKAGE / 'skills' / strategy / 'assets/windows-workflow.yml'
            self.assertEqual(target.read_bytes(), template.read_bytes())

    def test_artifact_is_complete_single_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            report = build(ROOT, output)
            archive_path = output / report['archive']
            self.assertEqual(hashlib.sha256(archive_path.read_bytes()).hexdigest(), report['sha256'])
            with zipfile.ZipFile(archive_path) as archive:
                expected = {p.relative_to(PACKAGE).as_posix() for p in package_files(PACKAGE)}
                self.assertEqual(set(archive.namelist()), expected)
                self.assertEqual(archive.namelist(), sorted(expected))
                self.assertIn('plugin.json', archive.namelist())
                self.assertIn('.app.json', archive.namelist())
                self.assertIn('LICENSE', archive.namelist())
                self.assertIn('assets/icon.png', archive.namelist())
                self.assertNotIn('.github/workflows/release.yml', archive.namelist())
                self.assertIsNone(archive.testzip())
                for info in archive.infolist():
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
            self.assertEqual((output / 'SHA256SUMS').read_text().strip(), report['sha256'] + '  ' + report['archive'])

    def test_build_ignores_mtime_but_not_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / 'fixture'
            package.mkdir()
            sample = package / 'sample.txt'
            sample.write_bytes(b'fixture\n')
            first = archive_bytes(package, root / 'first.zip')
            os.utime(sample, (1700000000, 1700000000))
            second = archive_bytes(package, root / 'second.zip')
            self.assertEqual(first, second)
            sample.write_bytes(b'changed\n')
            self.assertNotEqual(first, archive_bytes(package, root / 'third.zip'))

    def test_accidental_credential_file_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)
            (package / '.env').write_text('fixture only', encoding='utf-8')
            with self.assertRaises(ValueError):
                package_files(package)

    def test_ci_and_release_have_scoped_permissions(self) -> None:
        validate = yaml.safe_load((ROOT / '.github/workflows/validate.yml').read_text(encoding='utf-8'))
        release = yaml.safe_load((ROOT / '.github/workflows/release.yml').read_text(encoding='utf-8'))
        self.assertEqual(validate['permissions'], {'contents': 'read'})
        self.assertEqual(release['permissions'], {'contents': 'read'})
        self.assertEqual(set(validate['on']), {'push', 'pull_request', 'workflow_call'})
        self.assertEqual(release['on'], {'push': {'tags': ['v*']}})
        self.assertEqual(release['jobs']['publish']['needs'], ['validate'])
        self.assertEqual(release['jobs']['publish']['permissions'], {'contents': 'write'})
        self.assertIn('workflow_call', validate['on'])
        self.assertEqual(release['jobs']['validate']['uses'], './.github/workflows/validate.yml')

    def test_actions_are_pinned_and_no_credential_persistence(self) -> None:
        for path in (ROOT / '.github/workflows').glob('*.yml'):
            workflow = yaml.safe_load(path.read_text(encoding='utf-8'))
            for job in workflow['jobs'].values():
                for step in job.get('steps', []):
                    if 'uses' not in step:
                        continue
                    self.assertRegex(step['uses'], r'^actions/[a-z-]+@[0-9a-f]{40}$')
                    if step['uses'].startswith('actions/checkout@'):
                        self.assertIs(step['with']['persist-credentials'], False)

    def test_publisher_uses_verified_artifact_without_rebuild(self) -> None:
        release = yaml.safe_load((ROOT / '.github/workflows/release.yml').read_text(encoding='utf-8'))
        steps = release['jobs']['publish']['steps']
        self.assertTrue(any('download-artifact@' in step.get('uses', '') for step in steps))
        scripts = '\n'.join(step.get('run', '') for step in steps)
        self.assertIn('sha256sum --check', scripts)
        self.assertIn('--verify-tag', scripts)
        self.assertIn('--prerelease', scripts)
        self.assertNotIn('build_release.py', scripts)
        self.assertNotIn('--clobber', scripts)

    def test_no_second_ci_provider_or_publisher(self) -> None:
        self.assertFalse((ROOT / '.semaphore').exists())
        self.assertFalse((PACKAGE / '.github').exists())
        for path in (ROOT / '.github/workflows').glob('*.yml'):
            self.assertNotIn('OPENAI_API_KEY', path.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
