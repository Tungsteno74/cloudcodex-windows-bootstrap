"""Offline instruction-contract regressions, not a simulation of an agent or host."""
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "skills/github-actions-windows-bootstrap"
STRATEGIES = (
    "windows-ci-ephemeral-branch",
    "windows-ci-managed-branch",
    "windows-ci-fork-fallback",
)


def text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class ContinuityAndDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.router = text(ENTRY / "SKILL.md")
        cls.contract = text(ENTRY / "references/execution-contract.md")
        cls.access = text(ENTRY / "references/github-access.md")

    def test_entry_routes_to_discovery_without_sibling_paths(self) -> None:
        self.assertIn("apply Installed skill discovery", self.router)
        self.assertIn("not necessarily a callable tool", self.router)
        self.assertNotIn("../windows-ci-", self.router)

    def test_listing_omission_requires_targeted_lookup(self) -> None:
        for fragment in ("authority-filtered `skills.list`", "discovery hint, not proof of absence",
                         "one targeted read per supported route", "first verified success"):
            self.assertIn(fragment, self.contract)

    def test_discovery_requires_known_identity_release_and_scope(self) -> None:
        for fragment in ("installed metadata or caller evidence for the same plugin and release",
                         "Do not guess URI schemes", "Respect host authority/scope restrictions",
                         "Verify plugin identity, release and strategy name"):
            self.assertIn(fragment, self.contract)

    def test_denial_and_stale_version_do_not_trigger_bypass(self) -> None:
        for fragment in ("Stop at the first verified success, an access denial",
                         "at most one native metadata refresh", "never silently substitute old instructions",
                         "Do not turn a denial into a search for an alternative authorization route"):
            self.assertIn(fragment, self.contract)

    def test_package_editor_is_diagnostic_not_runtime_fallback(self) -> None:
        for fragment in ("do not substitute for loading the installed strategy",
                         "Plugin Creator is not a runtime dependency",
                         "Never silently invent a *different* strategy"):
            self.assertIn(fragment, self.contract)

    def test_optional_asset_synthesis_is_retained(self) -> None:
        self.assertIn("existing verified workflow synthesis remains available", self.contract)
        self.assertIn("missing required strategy instructions", self.contract)
        self.assertIn("WORKFLOW_MATERIALIZATION_UNVERIFIED", self.contract)
        self.assertNotIn("embedded_template", self.contract)

    def test_decisions_reuse_existing_state_with_provenance(self) -> None:
        for fragment in ("existing run journal and caller-returned handoff",
                         "verifiable user/parent grant reference", "expiry if any",
                         "revocation or supersession", "without asking for the same consent again"):
            self.assertIn(fragment, self.contract)

    def test_same_turn_change_does_not_enlarge_scope(self) -> None:
        self.assertIn("A new turn, phase or task does not itself revoke or enlarge a grant", self.contract)
        self.assertIn("Run-only grants never carry into another run", self.contract)
        self.assertIn("only when its explicit scope does so", self.contract)
        self.assertIn("parent carries verifiable provenance", self.contract)

    def test_revalidation_and_revocation_precede_reuse(self) -> None:
        for fragment in ("current instructions and provider permissions",
                         "Apply current restrictions and explicit revocation, expiry or supersession before reuse",
                         "An unverified record is evidence to reconcile, not permission",
                         "Provider approvals remain independent"):
            self.assertIn(fragment, self.contract)

    def test_preference_and_permissions_are_not_consent(self) -> None:
        self.assertIn("silence or technical push permission is not consent", self.contract)
        self.assertIn("does not persist an inferred CONFIRM/AUTO default", self.contract)
        self.assertIn("AUTO is routing preference, not permission expansion", self.router)

    def test_context_durability_and_secret_boundaries(self) -> None:
        for fragment in ("Never record secret values or authentication headers",
                         "Do not transfer credentials between channels, users, devices or environments",
                         "`volatile` for temporary files", "`durable` only when persistence was confirmed",
                         "export the minimum verified decision context"):
            self.assertIn(fragment, self.contract)

    def test_account_selection_uses_valid_decision_before_ambiguity(self) -> None:
        for fragment in ("Before treating selection as ambiguous", "Reuse the recorded authorized identity",
                         "Re-resolve host-local selectors from current metadata",
                         "out-of-scope operation still needs authorization"):
            self.assertIn(fragment, self.access)

    def test_push_trigger_does_not_require_dispatch_api(self) -> None:
        self.assertIn("a separate workflow-dispatch tool is not required", self.access)
        self.assertIn("Missing observation capability remains a blocker", self.access)
        self.assertIn("successful ref write is not a pass", self.access)

    def test_new_result_fields_are_present_once(self) -> None:
        for field in ("skill_discovery_status:", "skill_discovery_evidence:",
                      "decision_context_status:", "decision_context_locator:",
                      "decision_context_durability:", "authorization_origin:", "authorization_scope:"):
            self.assertEqual(self.contract.count(field), 1, field)

    def test_guarded_reconstruction_requires_authoritative_invariants(self) -> None:
        for phrase in (
            "Guarded same-strategy reconstruction",
            "without an explicit denial",
            "already loaded authoritative",
            "required safeguard",
            "AUTHORIZATION_REQUIRED",
            "handoff_status: returned_to_caller",
            "strategy_materialization: reconstructed",
            "No remote write",
        ):
            self.assertIn(phrase.lower(), self.contract.lower())
        self.assertIn("same-strategy reconstruction", self.router)
        self.assertNotIn("Do not synthesize a whole strategy", self.contract)

    def test_reconstructed_strategies_keep_cleanup_guards(self) -> None:
        for phrase in (
            "codex/windows-ci/<run-id>",
            "delete_ref",
            "Ephemeral retained",
            "Managed branch",
            "codex/windows-ci-managed",
            "codex-windows-ci-managed.yml",
            "cloudcodex-windows-bootstrap managed baseline v1",
            "cloudcodex-windows-bootstrap managed ci v1",
            "expected_sha",
            "Fork fallback",
            "preserved visibility",
            "Unknown marker/tip blocks",
        ):
            self.assertIn(phrase, self.contract)

    def test_runtime_resilience_has_no_specific_version_instructions(self) -> None:
        runtime = text(ROOT.parent.parent / "docs/runtime-resilience.md")
        self.assertNotIn("version 0.6.", runtime.lower())
        self.assertIn("return BLOCKED or AUTHORIZATION_REQUIRED", runtime)

    def test_shared_contracts_are_distributed_without_yaml_changes(self) -> None:
        for strategy in STRATEGIES:
            for filename in ("execution-contract.md", "github-access.md"):
                local = ROOT / "skills" / strategy / "references" / filename
                self.assertEqual(local.read_bytes(), (ENTRY / "references" / filename).read_bytes())
            asset = ROOT / "skills" / strategy / "assets/windows-workflow.yml"
            self.assertEqual(asset.read_bytes(), (ENTRY / "assets/windows-workflow.yml").read_bytes())


if __name__ == "__main__":
    unittest.main()
