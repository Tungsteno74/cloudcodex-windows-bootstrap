# GitHub access - connector-first contract

Prefer native GitHub connector operations. This contract is copied into each
execution strategy so a strategy never needs a sibling-skill file at runtime.

## 1. Discover the declared app and select the account

The package requires the existing GitHub app. Discover tools in the CURRENT host.
An installed plugin or loaded skill is not evidence of API access. If initial
repository/Actions tools are unavailable, report `GITHUB_TOOLS_UNAVAILABLE`.
During confirmed onboarding with inspected source and no remote writes, the entry
skill may return DEFERRED_TO_TASK; in a normal task or unknown phase return BLOCKED.

Use account metadata actually exposed by the tools. Do not hardcode selectors,
select by nickname/list order or infer repository owner equals acting account.
Ask if multiple identities could perform a write and intent is ambiguous. Never
print selectors, tokens, credential files or auth headers.

Before treating selection as ambiguous, apply Decision continuity in the execution
contract. Reuse the recorded authorized identity when provenance, scope and current
permissions remain valid; the presence of other accounts is not by itself a reason
to ask again. Re-resolve host-local selectors from current metadata, never from a
secret or stale selector saved in the journal. A newly required identity or an
out-of-scope operation still needs authorization.

## 2. Two narrow read checks, no permission-test writes

Prefer native GitHub connector operations to terminal HTTP or `gh api`.
Read exact repository metadata and relevant Actions runs with bounded GET-only
operations. Metadata `push: true` is not proof of Workflows write scope. Zero runs
is a successful empty result, not Forbidden.

If terminal HTTP failed but connector reads succeed, record
`github_access_status: read_verified`; do not request tokens merely to repeat a
supported request.

## 3. Plan callable routes before mutation

Discover only capabilities needed by the selected strategy. Tool existence and
provider permission are separate.

When a specialized GitHub read tool covers only part of the required collection
(for example PR-only workflow runs), inspect other exposed read-only connector
routes, including approved generic REST GET fetches. A narrow tool result is not
proof that the underlying capability is absent. Before terminal BLOCKED, check
eligible strategy fallbacks and report the exact missing route or verified denial.
Do not invent endpoints, bypass provider/host restrictions or broaden access.

- Source/ref/tree read: get_repo/file/commit/tree reads or approved **GET-only** fetch.
- CI objects: `create_tree` + `create_commit` from pinned source tree/parent.
- Branch publication: `create_branch` only after the complete CI SHA exists.
- Actions observation: run collection filtered by branch/SHA, then jobs/logs.
- Actions scheduling: an eligible verified `on.push` workflow is triggered by its
  authorized ref publication; a separate workflow-dispatch tool is not required.
  Verify trigger eligibility and an observation route before publishing. Missing
  observation capability remains a blocker, and a successful ref write is not a pass.
- Strict cleanup: actual ref deletion or independently authorized existing Git transport;
  `delete_file` is not branch deletion.
- Managed movement: `update_ref` with exact `expected_sha` and forced lease semantics;
  never represent `update_ref` as deletion.
- Fork: Discover actual fork creation/settings/cleanup capabilities first.

For Git-data creation, use `base_tree_sha` from the pinned source tree and explicit
`parent_sha`. Keep source SHA, tree SHA, baseline SHA and CI SHA distinct. A
successful write does NOT prove a Windows run occurred; observe the actual run.
No wildcard/mirror/default-branch push.

## 4. Ref deletion is a strategy constraint, not a global failure

If delete_ref is absent, `ephemeral_strict` returns `REF_DELETE_UNAVAILABLE` before
remote writes. That is a strategy constraint, not a global failure. The router may
ask for retained/managed/stop; AUTO may try managed, eligible fork, then retained.
`update_ref` may neutralize or manage a retained branch but does not delete it.

## 5. Existing terminal/Git transport

Use an ALREADY configured and authorized terminal/Git transport only when identity
and scope are established and it does not bypass a denial. Do not copy connector credentials, start new login flows, enlarge scopes or change app permissions.

## 6. Reconcile ambiguous write outcomes

A host/tool response such as timeout, cancellation, `approval required`, stale task
state, or generic failure can be provisional. It does not prove the provider rejected
the mutation. Preserve the same run identifiers and perform bounded GET-only read-back
for the exact ref/tip, marker commit, workflow path and branch+CI-SHA run before any
retry or terminal no-write report. If provider state confirms the operation, continue
from that state. Treat absence as confirmed only when every possible effect is
observable or the provider guarantees an atomic no-op; an unreferenced object with no
returned ID/SHA remains inconclusive. Retry at most once when absence is confirmed and
the operation remains authorized. Otherwise stop without duplicate writes and report
reconciliation risk.

## 7. Diagnose the failing layer

Keep operation/channel/status/evidence. Use these classifications where supported:
`GITHUB_TOOLS_UNAVAILABLE`, `RATE_LIMITED`, `OPERATION_PERMISSION_DENIED`,
`FORBIDDEN_UNCLASSIFIED`, `REF_DELETE_UNAVAILABLE`, `MANAGED_UPDATE_UNAVAILABLE`.
A bare 403 has no inferred cause or fallback. Zero runs is a successful empty result.
Stop strategy hopping on unclassified errors, account failures, rate limits,
global outages, test failures and active/PENDING runs.
