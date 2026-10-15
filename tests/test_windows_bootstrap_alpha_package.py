"""Offline contracts for the independently importable alpha package."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
STABLE = ROOT / "plugins" / "cloudcodex-windows-bootstrap"
ALPHA = ROOT / "plugins" / "cloudcodex-windows-bootstrap-alpha"
BASE = "ed300ffb1f3667f66e736e9114a1ceee669bcaed"
INSTALLER = ROOT / "tools" / "install_current_cloud_skills_alpha.sh"
ALPHA_SKILLS = (
    "codex-cloud-windows-check-probe-alpha",
    "github-actions-windows-bootstrap-alpha",
    "windows-ci-ephemeral-branch-alpha",
    "windows-ci-fork-fallback-alpha",
    "windows-ci-managed-branch-alpha",
    "current-cloud-windows-bootstrap-alpha-onboarding",
)

sys.path.insert(0, str(ROOT / "tools"))
from build_alpha_plugin import archive_bytes, build, package_files  # noqa: E402


class WindowsBootstrapAlphaPackageTests(unittest.TestCase):
    def test_v1_v2_identity_and_github_binding_are_in_sync(self) -> None:
        portable = json.loads((ALPHA / "plugin.json").read_text(encoding="utf-8"))
        native = json.loads((ALPHA / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(portable["name"], "cloudcodex-windows-bootstrap-alpha")
        self.assertEqual(portable["version"], "0.7.0-alpha.1")
        self.assertEqual(native["name"], portable["name"])
        self.assertEqual(native["version"], portable["version"])
        self.assertEqual(native["interface"], portable["extensions"]["com.openai"]["interface"])
        self.assertEqual(
            json.loads((ALPHA / ".app.json").read_text(encoding="utf-8")),
            json.loads((STABLE / ".app.json").read_text(encoding="utf-8")),
        )

    def test_six_unambiguous_alpha_skill_bundles(self) -> None:
        paths = sorted((ALPHA / "skills").glob("*/SKILL.md"))
        self.assertEqual(tuple(path.parent.name for path in paths), tuple(sorted(ALPHA_SKILLS)))
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertRegex(text, rf"(?m)^name: {re.escape(path.parent.name)}$")
        for name in ALPHA_SKILLS:
            self.assertTrue((ALPHA / "skills" / name / "agents" / "openai.yaml").is_file())
        for path in (ALPHA / "skills").rglob("*"):
            if path.suffix not in {".md", ".yaml"}:
                continue
            text = path.read_text(encoding="utf-8")
            for name in ALPHA_SKILLS[:5]:
                stable_name = re.escape(name.removesuffix("-alpha"))
                self.assertIsNone(re.search(rf"\${stable_name}(?!-alpha)\b", text), path)

    def test_onboarding_contract_is_guarded_and_asset_is_exact(self) -> None:
        root = ALPHA / "skills" / "current-cloud-windows-bootstrap-alpha-onboarding"
        asset = root / "assets" / "install_current_cloud_skills_alpha.sh"
        text = (root / "SKILL.md").read_text(encoding="utf-8")
        contract = (root / "references" / "onboarding-contract.md").read_text(encoding="utf-8")
        self.assertEqual(asset.read_bytes(), INSTALLER.read_bytes())
        for required in (
            "Cloud Current", "explicitly requested", "install_script", "startup",
            "start_skill", "ALPHA_INSTALL_DRAFT_BLOCKED", "ALPHA_INSTALL_DRAFT_MERGE_NEEDED",
            "Never publish", "read-back",
        ):
            self.assertIn(required, text + contract)
        self.assertIn("allow_implicit_invocation: false", (root / "agents" / "openai.yaml").read_text(encoding="utf-8"))

    def test_copied_workflow_assets_remain_byte_identical(self) -> None:
        bootstrap = "github-actions-windows-bootstrap"
        stable_asset = STABLE / "skills" / bootstrap / "assets" / "windows-workflow.yml"
        for name in (
            bootstrap,
            "windows-ci-ephemeral-branch",
            "windows-ci-fork-fallback",
            "windows-ci-managed-branch",
        ):
            alpha_asset = ALPHA / "skills" / f"{name}-alpha" / "assets" / "windows-workflow.yml"
            self.assertEqual(alpha_asset.read_bytes(), stable_asset.read_bytes(), name)

    def test_stable_package_is_byte_identical_to_requested_base(self) -> None:
        expected = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", BASE, "--", "plugins/cloudcodex-windows-bootstrap"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        ).stdout.splitlines()
        current = [
            str(path.relative_to(ROOT)).replace("\\", "/")
            for path in STABLE.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        ]
        self.assertEqual(sorted(current), sorted(expected))
        for relative in expected:
            observed = (ROOT / relative).read_bytes()
            baseline = subprocess.run(
                ["git", "show", f"{BASE}:{relative}"], cwd=ROOT, check=True, capture_output=True,
            ).stdout
            self.assertEqual(hashlib.sha256(observed).digest(), hashlib.sha256(baseline).digest(), relative)

    def test_resources_links_and_archive_are_complete_and_deterministic(self) -> None:
        for path in ALPHA.rglob("*.md"):
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (path.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(resolved.is_file(), f"{path}: {target}")
                self.assertIn(ALPHA.resolve(), resolved.parents)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            first = build(output)
            second = build(output / "second")
            self.assertEqual(first["sha256"], second["sha256"])
            archive = output / str(first["archive"])
            with zipfile.ZipFile(archive) as zipped:
                expected = {path.relative_to(ALPHA).as_posix() for path in package_files()}
                self.assertEqual(zipped.namelist(), sorted(expected))
                self.assertEqual(set(zipped.namelist()), expected)
                self.assertNotIn("cloudcodex-windows-bootstrap-alpha/plugin.json", zipped.namelist())
                self.assertIsNone(zipped.testzip())
            self.assertEqual(archive_bytes(ALPHA, output / "again.zip"), first["sha256"])

    def test_package_has_no_automatic_remote_write_or_api_claim(self) -> None:
        all_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in package_files() if path.suffix in {".md", ".yaml", ".json", ".sh"}
        )
        self.assertNotIn("curl | bash", all_text)
        self.assertIn("ALPHA_INSTALL_DRAFT_BLOCKED", all_text)
        self.assertIn("Never publish", all_text)
        self.assertIn("only an empty", all_text)


if __name__ == "__main__":
    unittest.main()
