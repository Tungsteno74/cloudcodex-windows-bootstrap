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

Prefer this skill's [local workflow template](references/windows-workflow.yml.template),
resolved from this skill root. Never use a sibling skill path, repository cwd, or Plugin
Creator at runtime.

If the auxiliary template is missing, unreadable or invalid, use the exact embedded YAML
below and report workflow_materialization: embedded_template. Do not improvise a
workflow merely because a bundled resource was not mounted. Both routes must preserve
the exact branch trigger, one bounded windows-latest job with pwsh, contents-read
permissions, full-SHA verified actions, checkout of the exact source commit with
credentials disabled and HEAD assertion, approved Windows checks, and explicit native-
command failure propagation.

Only if neither template can be used may a workflow be synthesized, and only if every
invariant can still be verified. Validate YAML, all substitutions, pins, check commands
and the complete CI-only diff before any remote object/ref write. Otherwise return
WORKFLOW_MATERIALIZATION_UNVERIFIED.

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

## Embedded workflow template (Cloud resource-loading fallback)

This YAML is embedded in the loaded SKILL.md, with contents synchronized from the
canonical authoring template by the release validator. Use it only when the local
auxiliary template cannot be read. Substitute trusted literals and validate the
resulting workflow before publishing.

<!-- BEGIN SYNCED WINDOWS WORKFLOW TEMPLATE -->
```yaml
# TEMPLATE ONLY: substitute trusted literals and validate before committing.
name: Codex Windows CI __RUN_ID__
run-name: Windows checks __SOURCE_SHORT_SHA__ (__RUN_ID__)
"on":
  push:
    branches:
      - '__TEMP_BRANCH__'
permissions:
  contents: read
jobs:
  windows-validation:
    runs-on: windows-latest
    timeout-minutes: __TIMEOUT_MINUTES__
    defaults:
      run:
        shell: pwsh
    steps:
      - name: Checkout the exact source revision
        uses: actions/checkout@__CHECKOUT_ACTION_SHA__
        with:
          ref: '__SOURCE_SHA__'
          persist-credentials: false
      - name: Verify source identity
        env:
          EXPECTED_SOURCE_SHA: '__SOURCE_SHA__'
        run: |
          $ErrorActionPreference = 'Stop'
          $observed = git rev-parse HEAD
          if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
          if ($observed.Trim() -ne $env:EXPECTED_SOURCE_SHA) {
            throw 'Unexpected source revision; refusing to validate a different commit.'
          }
      # Insert only the language/tool setup required by the project, with verified pins.
      - name: Run the selected native Windows checks
        run: |
          $ErrorActionPreference = 'Stop'
          __WINDOWS_CHECK_COMMANDS__
```
<!-- END SYNCED WINDOWS WORKFLOW TEMPLATE -->
