"""Offline subprocess coverage for the isolated Current Cloud alpha installer."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "install_current_cloud_skills_alpha.sh"
SKILLS = (
    "codex-cloud-windows-check-probe",
    "github-actions-windows-bootstrap",
    "windows-ci-ephemeral-branch",
    "windows-ci-fork-fallback",
    "windows-ci-managed-branch",
)


def bash_executable() -> str | None:
    """Locate Bash on Linux or the standard Git for Windows installation."""
    configured = os.environ.get("BASH")
    candidates = [configured] if configured else []
    candidates.extend((r"C:\Program Files\Git\bin\bash.exe", shutil.which("bash")))
    return next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)


class CurrentCloudSkillInstallAlphaTests(unittest.TestCase):
    """Exercise copies, idempotency, collision handling, and early validation."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.bash = bash_executable()
        if cls.bash is None:
            raise unittest.SkipTest("Bash is required for the Linux/Bash alpha installer test.")

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        shutil.copytree(ROOT, self.source, ignore=shutil.ignore_patterns(".git", "dist", "__pycache__"))
        self.home = self.root / "home"
        self.home.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_installer(self, source: Path | None = None) -> subprocess.CompletedProcess[str]:
        environment = os.environ | {
            "HOME": str(self.home),
            "CURRENT_CLOUD_SKILLS_ALPHA_SOURCE": str(source or self.source),
        }
        return subprocess.run(
            [self.bash, str(SCRIPT)],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def installed(self, skill: str) -> Path:
        return self.home / ".agents" / "skills" / skill

    def test_copies_all_skill_directories_assets_and_references(self) -> None:
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        source_skills = self.source / "plugins" / "cloudcodex-windows-bootstrap" / "skills"
        for skill in SKILLS:
            with self.subTest(skill=skill):
                destination = self.installed(skill)
                self.assertTrue(destination.is_dir())
                self.assertFalse(destination.is_symlink())
                self.assertTrue((destination / "SKILL.md").is_file())
                self.assertTrue((destination / "agents" / "openai.yaml").is_file())
                self.assertFalse(any(path.is_symlink() for path in destination.rglob("*")))
                self.assertEqual(
                    sorted(path.relative_to(source_skills / skill) for path in (source_skills / skill).rglob("*")),
                    sorted(path.relative_to(destination) for path in destination.rglob("*")),
                )
                for source_file in (source_skills / skill).rglob("*"):
                    if source_file.is_file():
                        copied = destination / source_file.relative_to(source_skills / skill)
                        self.assertEqual(copied.read_bytes(), source_file.read_bytes())
        for skill in SKILLS[1:]:
            self.assertTrue((self.installed(skill) / "assets" / "windows-workflow.yml").is_file())
            self.assertTrue((self.installed(skill) / "references" / "execution-contract.md").is_file())

    def test_repeat_is_idempotent(self) -> None:
        self.assertEqual(self.run_installer().returncode, 0)
        second = self.run_installer()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("already installed and identical", second.stdout)

    def test_collision_is_not_clobbered(self) -> None:
        collision = self.installed(SKILLS[0])
        collision.mkdir(parents=True)
        sentinel = collision / "sentinel.txt"
        sentinel.write_text("keep", encoding="utf-8")
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertFalse(self.installed(SKILLS[1]).exists())

    def test_missing_asset_fails_before_partial_install(self) -> None:
        broken = self.root / "broken-source"
        shutil.copytree(self.source, broken)
        (broken / "plugins" / "cloudcodex-windows-bootstrap" / "skills" /
         "windows-ci-managed-branch" / "assets" / "windows-workflow.yml").unlink()
        result = self.run_installer(broken)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required file is missing", result.stderr)
        self.assertFalse((self.home / ".agents" / "skills").exists())


    def test_invalid_skill_frontmatter_fails_before_install(self) -> None:
        broken = self.root / "invalid-frontmatter"
        shutil.copytree(self.source, broken)
        skill_file = (
            broken / "plugins" / "cloudcodex-windows-bootstrap" /
            "skills" / "github-actions-windows-bootstrap" / "SKILL.md"
        )
        content = skill_file.read_text(encoding="utf-8")
        skill_file.write_text(content.replace(
            "name: github-actions-windows-bootstrap",
            "name: unexpected-skill-name",
            1,
        ), encoding="utf-8")
        result = self.run_installer(broken)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("name mismatch", result.stderr)
        self.assertFalse((self.home / ".agents" / "skills").exists())

    def test_wrong_plugin_version_fails_before_install(self) -> None:
        broken = self.root / "wrong-version"
        shutil.copytree(self.source, broken)
        manifest = (
            broken / "plugins" / "cloudcodex-windows-bootstrap" / "plugin.json"
        )
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                '"version": "0.6.7"', '"version": "0.0.0"', 1
            ),
            encoding="utf-8",
        )
        result = self.run_installer(broken)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plugin version is not", result.stderr)
        self.assertFalse((self.home / ".agents" / "skills").exists())

if __name__ == "__main__":
    unittest.main()
