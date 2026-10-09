from __future__ import annotations

import json
from pathlib import Path
import re
import struct
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'skills/github-actions-windows-bootstrap'
STRATEGIES = (
    'windows-ci-ephemeral-branch',
    'windows-ci-managed-branch',
    'windows-ci-fork-fallback',
)


def rendered_workflow(template_text: str | None = None) -> dict:
    text = (template_text if template_text is not None else
            (ENTRY / 'assets/windows-workflow.yml').read_text())
    values = {
        '__RUN_ID__': 'fixture-001',
        '__SOURCE_SHORT_SHA__': 'bbbbbbb',
        '__TEMP_BRANCH__': 'codex/windows-ci/fixture-001',
        '__TIMEOUT_MINUTES__': '15',
        '__CHECKOUT_ACTION_SHA__': 'a' * 40,
        '__SOURCE_SHA__': 'b' * 40,
        '__WINDOWS_CHECK_COMMANDS__': "python --version\n          if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }",
    }
    for key, value in values.items():
        text = text.replace(key, value)
    assert not re.search(r'__[A-Z_]+__', text)
    return yaml.safe_load(text)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / 'plugin.json').read_text())
        cls.overlay = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
        cls.entry = (ENTRY / 'SKILL.md').read_text()
        cls.contract = (ENTRY / 'references/execution-contract.md').read_text()
        cls.strategies = {
            name: (ROOT / 'skills' / name / 'SKILL.md').read_text()
            for name in STRATEGIES
        }

    def test_version_and_identity(self) -> None:
        self.assertEqual(self.manifest['name'], 'cloudcodex-windows-bootstrap')
        self.assertEqual(self.manifest['version'], '0.6.5')
        self.assertEqual(self.overlay['version'], '0.6.5')
        self.assertEqual(self.overlay['name'], self.manifest['name'])
        self.assertEqual(self.overlay['interface'], self.manifest['extensions']['com.openai']['interface'])

    def test_branding_asset(self) -> None:
        expected = './assets/icon.png'
        interface = self.manifest['extensions']['com.openai']['interface']
        self.assertEqual(interface['logo'], expected)
        self.assertEqual(interface['composerIcon'], expected)
        self.assertEqual(self.overlay['interface']['logo'], expected)
        self.assertEqual(self.overlay['interface']['composerIcon'], expected)

        icon = ROOT / expected.removeprefix('./')
        self.assertTrue(icon.is_file())
        data = icon.read_bytes()
        self.assertLessEqual(len(data), 5 * 1024 * 1024)
        self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
        self.assertEqual(data[12:16], b'IHDR')
        self.assertEqual(struct.unpack('>I', data[8:12])[0], 13)
        width, height, bit_depth, color_type, compression, filter_method, interlace = (
            struct.unpack('>IIBBBBB', data[16:29])
        )
        self.assertGreaterEqual(width, 256)
        self.assertGreaterEqual(height, 256)
        self.assertEqual(bit_depth, 8)
        self.assertIn(color_type, (4, 6), 'PNG must contain an alpha channel')
        self.assertEqual(compression, 0)
        self.assertEqual(filter_method, 0)
        self.assertIn(interlace, (0, 1))

    def test_default_prompt_preserved(self) -> None:
        expected = ('Use $github-actions-windows-bootstrap to validate or resume the recorded Windows-only gap. '
            'If delegated context or start_skill data is missing, return the exact repository, revision, '
            'checks, authorization, and interaction context needed by the parent without remote writes. '
            'Reconcile ambiguous provider outcomes before retrying or reporting no changes.')
        self.assertEqual(self.overlay['interface']['defaultPrompt'], expected)

    def test_operational_skills_implicit_probe_explicit(self) -> None:
        operational = {'github-actions-windows-bootstrap', *STRATEGIES}
        for name in operational:
            cfg = yaml.safe_load((ROOT / 'skills' / name / 'agents/openai.yaml').read_text())
            self.assertTrue(cfg['policy']['allow_implicit_invocation'], name)
            self.assertIn('CODEX', cfg['policy']['products'])
        probe = yaml.safe_load((ROOT / 'skills/codex-cloud-windows-check-probe/agents/openai.yaml').read_text())
        self.assertFalse(probe['policy']['allow_implicit_invocation'])

    def test_entry_dispatches_by_skill_name(self) -> None:
        for name in STRATEGIES:
            self.assertIn(f'${name}', self.entry)
        self.assertNotIn('../windows-ci-', self.entry)
        self.assertIn('Do not resolve sibling SKILL.md files manually', self.entry)

    def test_strategy_context_guards(self) -> None:
        for name, text in self.strategies.items():
            with self.subTest(name=name):
                self.assertIn('Router-context guard', text)
                self.assertIn('ROUTER_CONTEXT_REQUIRED', text)
                self.assertIn('$github-actions-windows-bootstrap', text)
                self.assertRegex(text, r'no remote\s+write|make no remote write')

    def test_reconciliation_contract_is_distributed(self) -> None:
        for phrase in ('Ambiguous control-plane outcomes and reconciliation',
                       'reconciliation_status:', 'Never claim no remote writes'):
            self.assertIn(phrase, self.contract)
        for name in STRATEGIES:
            local = ROOT / 'skills' / name / 'references/execution-contract.md'
            self.assertEqual(local.read_bytes(), (ENTRY / 'references/execution-contract.md').read_bytes())

    def test_no_invented_managed_state_dependency(self) -> None:
        managed = self.strategies['windows-ci-managed-branch']
        self.assertIn('No `managed-state.md` file is part of this', managed)
        for path in ROOT.rglob('*'):
            self.assertNotEqual(path.name, 'managed-state.md')

    def test_no_cross_skill_runtime_paths(self) -> None:
        for name, text in self.strategies.items():
            self.assertNotIn('../github-actions-windows-bootstrap', text, name)
            self.assertNotIn('../windows-ci-', text, name)

    def test_strategy_local_contracts_exist(self) -> None:
        refs = ('execution-contract.md', 'github-access.md', 'github-constraints.md')
        for name in STRATEGIES:
            root = ROOT / 'skills' / name / 'references'
            for ref in refs:
                self.assertTrue((root / ref).is_file(), f'{name}/{ref}')
            self.assertTrue((ROOT / 'skills' / name / 'assets/windows-workflow.yml').is_file())

    def test_local_contracts_match_canonical(self) -> None:
        canonical = ENTRY / 'references'
        for name in STRATEGIES:
            local = ROOT / 'skills' / name / 'references'
            for ref in ('execution-contract.md', 'github-access.md', 'github-constraints.md'):
                self.assertEqual((local / ref).read_bytes(), (canonical / ref).read_bytes())
            self.assertEqual((ROOT / 'skills' / name / 'assets/windows-workflow.yml').read_bytes(),
                             (ENTRY / 'assets/windows-workflow.yml').read_bytes())

    def test_context_aware_mode_precedence(self) -> None:
        ordered = [
            'explicit current-run user choice',
            'verified resumed same run',
            'positively identifies this execution as delegated',
            'directly interacting',
            'interaction context cannot be established',
        ]
        positions = [self.entry.index(text) for text in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('delegated_default', self.entry)
        self.assertIn('interactive_default', self.entry)
        self.assertIn('unknown_default', self.entry)
        self.assertIn('ESCALATION_MODE_SOURCE', self.entry)
        self.assertIn('INTERACTION_CONTEXT', self.entry)

    def test_delegated_detection_is_not_guessed_from_task_or_handoff(self) -> None:
        self.assertIn('Do **not** infer delegated execution merely because this is a Codex Cloud task', self.entry)
        self.assertIn('DEFERRED_TO_TASK', self.entry)
        self.assertIn('Positive evidence', self.entry)
        self.assertIn('If such evidence is absent, choose CONFIRM', self.entry)

    def test_auto_does_not_expand_authorization(self) -> None:
        for phrase in ('AUTO is routing preference, not permission expansion',
                       'new credentials', 'broader scopes', 'provider/host approvals',
                       'AUTHORIZATION_REQUIRED'):
            self.assertIn(phrase, self.entry)
        self.assertIn('does not suppress host/provider approvals', ' '.join(self.contract.split()))

    def test_cross_phase_default_is_recomputed(self) -> None:
        self.assertIn('Do not carry an onboarding **default** CONFIRM/AUTO', self.entry)
        self.assertIn('recompute the default from the actual\nnew task context', self.entry)
        self.assertIn('must not freeze a later delegated task into CONFIRM', self.contract)

    def test_deferred_is_neither_consent_nor_prohibition(self) -> None:
        self.assertIn('not write authorization', self.contract)
        self.assertIn('not a\nprohibition on later writes', self.contract)
        self.assertIn('Under CONFIRM, ask before the first strategy side effect', self.contract)
        self.assertIn('not a prohibition on later writes', ' '.join(self.entry.split()))

    def test_workflow_fixture_shape(self) -> None:
        wf = rendered_workflow()
        self.assertEqual(wf['on'], {'push': {'branches': ['codex/windows-ci/fixture-001']}})
        self.assertEqual(wf['permissions'], {'contents': 'read'})
        job = wf['jobs']['windows-validation']
        self.assertEqual(job['runs-on'], 'windows-latest')
        self.assertEqual(job['timeout-minutes'], 15)
        self.assertEqual(job['defaults']['run']['shell'], 'pwsh')
        checkout = job['steps'][0]
        self.assertRegex(checkout['uses'], r'^actions/checkout@[0-9a-f]{40}$')
        self.assertEqual(checkout['with']['ref'], 'b' * 40)
        self.assertIs(checkout['with']['persist-credentials'], False)

    def test_workflow_assets_are_canonical_and_not_embedded(self) -> None:
        canonical = (ENTRY / 'assets/windows-workflow.yml').read_bytes()
        self.assertEqual(len(canonical), 1248)
        self.assertNotIn(b'\r', canonical)
        self.assertFalse(canonical.startswith(b'\xef\xbb\xbf'))
        for name, skill_text in self.strategies.items():
            with self.subTest(name=name):
                template_path = ROOT / 'skills' / name / 'assets/windows-workflow.yml'
                self.assertEqual(template_path.read_bytes(), canonical)
                self.assertIn('assets/windows-workflow.yml', skill_text)
                self.assertIn('synthesized', skill_text)
                self.assertNotIn('BEGIN SYNCED WINDOWS WORKFLOW TEMPLATE', skill_text)
                self.assertNotIn('embedded_template', skill_text)
        workflow = rendered_workflow(canonical.decode('utf-8'))
        self.assertEqual(workflow['on']['push']['branches'],
                         ['codex/windows-ci/fixture-001'])
        self.assertEqual(workflow['permissions'], {'contents': 'read'})
        self.assertEqual(workflow['jobs']['windows-validation']['runs-on'],
                         'windows-latest')

    def test_no_default_branch_or_pr_workflow(self) -> None:
        for name, text in self.strategies.items():
            self.assertNotIn('open a pull request', text.lower(), name)
            self.assertIn('default branch', text.lower(), name)
        self.assertIn('never merges or writes', (ROOT / 'README.md').read_text())


if __name__ == '__main__':
    unittest.main()
