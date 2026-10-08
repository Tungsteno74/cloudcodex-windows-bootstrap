---
name: windows-ci-managed-branch
description: >-
  Managed-branch Windows CI strategy for an active github-actions-windows-bootstrap
  run, normally after strict ephemeral reports REF_DELETE_UNAVAILABLE and the same
  run selected managed via CONFIRM or AUTO. May be selected implicitly only with a
  valid bootstrap context. Never write without that context.
---

# Windows CI — managed branch

Read this skill's local [execution contract](references/execution-contract.md),
[GitHub access contract](references/github-access.md), and
[provider constraints](references/github-constraints.md). Do not depend on sibling
skill files.

## Router-context guard

Require valid bootstrap context: run id, phase, repository/full source SHA,
CONFIRM/AUTO state, managed strategy authorization/routing, test plan/postconditions,
GitHub channel/account and authorization state. Without it, make no remote write;
invoke `$github-actions-windows-bootstrap` or return `ROUTER_CONTEXT_REQUIRED`.
Implicit availability is never write authorization.

## Purpose and fixed resources

Use one persistent branch `codex/windows-ci-managed` and workflow path
`.github/workflows/codex-windows-ci-managed.yml`.
At rest the branch points to a managed baseline commit whose tree equals its source
parent exactly and contains no plugin workflow change.

Markers:
- `cloudcodex-windows-bootstrap managed baseline v1`
- `cloudcodex-windows-bootstrap managed ci v1`

Do not treat branch name alone as ownership proof. Provider refs/marker commits and
the run journal are the managed state. No `managed-state.md` file is part of this
contract; do not probe, invent, or create that path.

## Eligibility and ownership

Require source/tree/ref read, create_tree/create_commit, create_branch if absent,
Actions observation, and an `update_ref`-equivalent operation supporting
expected-SHA + forced lease semantics. Ref deletion is not required. If safe update
is unavailable return `MANAGED_UPDATE_UNAVAILABLE` before publication.

Inspect automation for both publication and baseline-restoration pushes. Unsafe
existing automation => `UNSAFE_EXISTING_AUTOMATION`. If source already owns the
stable workflow path => `MANAGED_WORKFLOW_PATH_CONFLICT`.

If managed branch exists, reuse only when tip is a marker baseline, has one parent,
its tree SHA equals parent tree SHA, no required run is active, and the lease uses
that exact observed tip. Interrupted CI tip may be recovered only with proven
marker/parent/terminal run. Otherwise `MANAGED_BRANCH_CONFLICT`; never force unknown.

## Local workflow materialization

Prefer this skill's local YAML workflow asset at
[assets/windows-workflow.yml](assets/windows-workflow.yml), resolved from its
observed skill root or actual registered resource URI. Do not use a sibling
skill path, repository cwd, or Plugin Creator at runtime.

Validate the template before use: exact strategy branch push trigger, one
bounded GitHub-hosted Windows runner and PowerShell job, contents-read only,
no secrets/OIDC/write token, SHA-pinned verified actions, exact source_revision
checkout with persist-credentials disabled and HEAD identity assertion, only
approved Windows checks and explicit native-command failure propagation.
Substitute all placeholders and inspect the complete CI-only diff.

If the asset is unavailable or invalid, synthesis from the mandatory workflow
invariants is permitted only as exceptional recovery. Never claim the asset
was read when it was not. If the synthesized workflow cannot be independently
verified against all invariants, return WORKFLOW_MATERIALIZATION_UNVERIFIED
without remote writes. Report workflow_materialization: local_template when
reading the verified asset, or synthesized for independently verified fallback.
Neither path grants new authorization.

## Execute

1. Materialize and validate workflow for `codex/windows-ci-managed` before any
   remote object/ref write; review the CI-only diff.
2. Create new baseline commit with exact source tree and source parent; no file diff.
3. Create CI tree adding only the stable workflow/indispensable reviewed helper;
   create CI commit with new baseline parent. Workflow checks out exact source SHA.
4. Verify returned baseline/CI tree, parents and diff.
5. Publish once:
   - branch absent: create directly at CI SHA;
   - valid baseline: update from observed baseline to CI SHA using
     `expected_sha=<observed_baseline>` and `force=true`.
   Never update default branch, open a PR or merge.
6. Observe Actions by branch + CI SHA + workflow path. PENDING keeps CI tip.
7. After terminal run, restore CI SHA -> new baseline using
   `expected_sha=<ci_sha>`, `force=true`; verify final tip/tree and report
   `retention: managed_baseline`.
8. If any write-capable call has an ambiguous/approval/timeout outcome, apply the
   shared provider-state reconciliation contract before retry, next step or terminal
   reporting. Never duplicate baseline/CI commits or claim no remote writes from tool
   status alone.

If reset fails or tip changed, `cleanup: required`; do not start another execution
strategy after managed published or started a run. FAILED_CHECKS is final evidence,
not escalation.
