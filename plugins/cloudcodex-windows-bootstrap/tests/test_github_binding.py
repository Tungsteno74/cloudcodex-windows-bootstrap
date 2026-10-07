from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / 'skills/github-actions-windows-bootstrap'
APP_ID = 'connector_76869538009648d5b282a4bb21c3d157'


class GitHubBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.apps = json.loads((ROOT / '.app.json').read_text())
        cls.entry = (ENTRY / 'SKILL.md').read_text()
        cls.access = (ENTRY / 'references/github-access.md').read_text()
        cls.contract = (ENTRY / 'references/execution-contract.md').read_text()

    def test_required_app(self) -> None:
        self.assertEqual(self.apps, {'apps': {'github': {'id': APP_ID, 'required': True}}})

    def test_connector_first_and_account_selection(self) -> None:
        self.assertIn('Prefer native GitHub connector operations', self.access)
        self.assertIn('Do not hardcode selectors', self.access)
        self.assertIn('nickname/list order', self.access)
        self.assertIn('Ask if multiple identities could perform a write', self.access)
        self.assertIn('push: true', self.access)
        self.assertIn('not proof of Workflows write scope', self.access)

    def test_no_auth_workaround(self) -> None:
        for phrase in ('ALREADY configured and authorized', 'does not bypass a denial',
                       'connector credentials', 'new login flows', 'enlarge scopes'):
            self.assertIn(phrase, self.access)

    def test_error_taxonomy(self) -> None:
        for phrase in ('GITHUB_TOOLS_UNAVAILABLE', 'RATE_LIMITED',
                       'OPERATION_PERMISSION_DENIED', 'FORBIDDEN_UNCLASSIFIED',
                       'REF_DELETE_UNAVAILABLE', 'MANAGED_UPDATE_UNAVAILABLE'):
            self.assertIn(phrase, self.access)

    def test_contract_records_channel_and_operation(self) -> None:
        for field in ('github_channel:', 'github_account:', 'github_access_status:',
                      'failed_operation:', 'http_status:', 'error_origin:', 'error_reason:'):
            self.assertIn(field, self.contract)


if __name__ == '__main__':
    unittest.main()
