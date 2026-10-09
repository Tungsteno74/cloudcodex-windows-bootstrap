from __future__ import annotations

from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'skills/github-actions-windows-bootstrap'
STRATEGIES = ('windows-ci-ephemeral-branch','windows-ci-managed-branch','windows-ci-fork-fallback')


class DispatchAndHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = (ENTRY / 'SKILL.md').read_text()
        cls.contract = (ENTRY / 'references/execution-contract.md').read_text()

    def test_trigger_covers_onboarding_and_normal_task(self) -> None:
        meta = yaml.safe_load(self.entry.split('---', 2)[1])
        self.assertIn('onboarding', meta['description'])
        self.assertIn('DEFERRED_TO_TASK', meta['description'])
        self.assertIn('normal task', meta['description'])

    def test_entry_and_strategies_are_implicit(self) -> None:
        for name in ('github-actions-windows-bootstrap', *STRATEGIES):
            cfg = yaml.safe_load((ROOT / 'skills' / name / 'agents/openai.yaml').read_text())
            self.assertTrue(cfg['policy']['allow_implicit_invocation'])

    def test_strategy_description_is_context_gated(self) -> None:
        for name in STRATEGIES:
            text = (ROOT / 'skills' / name / 'SKILL.md').read_text()
            front = yaml.safe_load(text.split('---', 2)[1])
            self.assertIn('bootstrap', front['description'].lower())
            self.assertIn('context', front['description'].lower())
            self.assertIn('ROUTER_CONTEXT_REQUIRED', text)

    def test_delegated_default_requires_positive_evidence(self) -> None:
        for phrase in ('delegated_default', 'Positive evidence',
                       'Codex Cloud task', 'DEFERRED_TO_TASK',
                       'If such evidence is absent, choose CONFIRM'):
            self.assertIn(phrase, self.entry)

    def test_explicit_mode_outranks_defaults(self) -> None:
        explicit = self.entry.index('explicit current-run user choice')
        delegated = self.entry.index('positively identifies this execution as delegated')
        interactive = self.entry.index('directly interacting')
        self.assertLess(explicit, delegated)
        self.assertLess(delegated, interactive)

    def test_delegated_auto_does_not_pause_for_strategy_choice(self) -> None:
        self.assertIn('must not emit AWAITING_CONFIRMATION merely because multiple eligible plugin\nstrategies exist', self.entry)
        self.assertIn('AUTHORIZATION_REQUIRED', self.entry)
        self.assertIn('AUTO is routing preference, not permission expansion', self.entry)

    def test_handoff_only_for_host_capability_gap(self) -> None:
        for phrase in ('phase is positively identified as environment onboarding',
                       'capability_missing', 'no provider denial',
                       'created no remote objects'):
            self.assertIn(phrase, self.entry)
        for phrase in ('FAILED_CHECKS', 'RATE_LIMITED', 'FORBIDDEN_UNCLASSIFIED', 'PENDING'):
            self.assertIn(phrase, self.entry)

    def test_resume_recomputes_default_but_preserves_explicit_choice(self) -> None:
        self.assertIn('Preserve only an\n> explicit user mode choice', self.entry)
        self.assertIn('Do not carry an onboarding **default** CONFIRM/AUTO', self.entry)
        self.assertIn('DEFERRED_TO_TASK by itself does not prove', ' '.join(self.entry.replace('`', '').split()))
        self.assertIn('must not freeze a later delegated task into CONFIRM', self.contract)

    def test_setup_refresh_warning_is_not_global_failure(self) -> None:
        self.assertIn('setup refresh had errors', self.entry)
        self.assertIn('Do not recreate or republish an environment', self.entry)

    def test_missing_handoff_returns_structured_context(self) -> None:
        for phrase in ('Missing or stale handoff context', 'handoff_status: returned_to_caller',
                       'repository, full source SHA, checks, authorization scope'):
            self.assertIn(phrase, self.entry)
        self.assertIn('start_skill` is an optimization', self.entry)

    def test_ambiguous_write_requires_provider_reconciliation(self) -> None:
        for phrase in ('provider-state reconciliation', 'Never claim no remote writes',
                       'reconciliation_status:', 'never duplicate', 'unreferenced object'):
            self.assertIn(phrase.lower(), (self.entry + self.contract).lower())

    def test_strategy_order_preserved(self) -> None:
        auto = self.entry.split('### AUTO',1)[1].split('## 5.',1)[0]
        self.assertLess(auto.index('$windows-ci-managed-branch'), auto.index('$windows-ci-fork-fallback'))
        self.assertLess(auto.index('$windows-ci-fork-fallback'), auto.index('ephemeral_retained'))

    def test_contract_version_and_fields(self) -> None:
        self.assertIn('plugin_version: 0.6.5', self.contract)
        self.assertIn('INTERACTION_CONTEXT:', self.contract)
        self.assertIn('ESCALATION_MODE_SOURCE:', self.contract)
        self.assertIn('assets/windows-workflow.yml', self.contract)
        self.assertIn('local_template', self.contract)
        self.assertNotIn('embedded_template', self.contract)


if __name__ == '__main__':
    unittest.main()
