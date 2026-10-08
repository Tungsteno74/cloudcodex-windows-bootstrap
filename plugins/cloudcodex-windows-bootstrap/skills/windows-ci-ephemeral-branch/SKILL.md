---
name: windows-ci-ephemeral-branch
description: >-
  Windows CI strategy for an active github-actions-windows-bootstrap run. Prefer
  strict temporary-branch cleanup; retained mode is allowed only after the same
  run's CONFIRM choice or AUTO terminal routing. May be selected implicitly only
  when a valid bootstrap run context exists. Never write without that context.
---

# Windows CI — ephemeral branch

Read this skill's local [execution contract](references/execution-contract.md),
[GitHub access contract](references/github-access.md), and
[provider constraints](references/github-constraints.md). Do not read contracts
from a sibling skill.

## Router-context guard

Require a valid bootstrap run context containing `run_id`, phase, source repository,
full `source_revision`, escalation mode, selected test plan/postconditions, GitHub
channel/account state and authorization state. Also require `ephemeral_mode` to be
`ephemeral_strict` or `ephemeral_retained`.

If context is absent, ambiguous or belongs to another revision/run, make **no remote
write**. Load/invoke `$github-actions-windows-bootstrap` to establish or resume it;
if that is unavailable return `ROUTER_CONTEXT_REQUIRED`. Never infer write consent
from this skill's implicit availability.

## Eligibility and modes

Use the selected authorized channel and verify publication + Actions observation.

### `ephemeral_strict` — default

Require a real ref-delete operation or independently authorized existing Git
transport able to delete exactly the run-owned ref. `delete_file` and `update_ref`
are not branch deletion. If unavailable, return `REF_DELETE_UNAVAILABLE` before
creating remote Git objects/refs and let the bootstrap router decide.

### `ephemeral_retained` — cleanup-degraded

Proceed without ref deletion only when the same run records either:
- CONFIRM: user explicitly selected retained branch; or
- AUTO: router reached retained as terminal fallback.

Before writing, disclose the exact branch and that it may remain. This mode cannot
bypass missing publication/Actions access, an explicit prohibition, or an unrelated
blocker.

Inspect existing automation for push/create/update effects. If a push could deploy,
expose secrets/self-hosted runners or create unbounded unrelated side effects, stop
with `UNSAFE_EXISTING_AUTOMATION`; do not disable unrelated workflows.

## Local workflow materialization

Prefer this skill's [local workflow template](references/windows-workflow.yml.template).
Resolve it against the observed skill root, never the repository cwd or a sibling
skill. Do not invent plugin IDs or mount paths or require Plugin Creator at runtime.

If the auxiliary template is unreadable, missing or invalid, use the exact embedded
YAML below and report workflow_materialization: embedded_template. Do not construct
the YAML from prose merely because the auxiliary resource cannot be mounted.
Verify all mandatory invariants:

- an exact literal branch-only push trigger;
- one bounded GitHub-hosted windows-latest job with pwsh;
- contents-read permissions, no secrets, OIDC, write tokens or self-hosted runners;
- exact source_revision checkout, persist-credentials: false and HEAD assertion;
- trusted actions pinned to verified full SHA values;
- only approved Windows checks and required setup;
- explicit native-command failure propagation;
- valid YAML, no unresolved placeholders and a reviewed CI-only diff before
  any remote Git object/ref write.

Only if both templates are unusable may the existing verified-synthesis fallback
be applied. If any invariant cannot be verified, return
WORKFLOW_MATERIALIZATION_UNVERIFIED. Materialization does not change strategy
selection or authorization.

## Execute

1. Resolve source SHA/default tip; use unique ref `codex/windows-ci/<run-id>` and
   workflow `.github/workflows/codex-windows-ci-<run-id>.yml`; reject collisions
   unless proven to belong to this same interrupted run.
2. Materialize/validate one CI-only workflow from the source tree. Preserve app
   code, tests and AGENTS.md.
3. Create the CI tree/commit with source parent, verify tree/parent/diff, then create
   the unique branch at the complete CI SHA. No wildcard/mirror/default-branch push,
   force-overwrite, PR or merge. Never write merely to test permission.
4. Correlate the run by repository + branch + full CI SHA + workflow path and
   observe boundedly. PENDING preserves the ref and never triggers another strategy.
5. After a terminal run:
   - strict: delete only the run-owned branch when its tip is exactly the expected
     CI SHA; unexpected cleanup failure => `cleanup: required`;
   - retained: never claim deletion. If safe `update_ref` exists and tip == CI SHA,
     move to exact source SHA with `expected_sha=<ci_sha>`, `force=true` and report
     `retention: retained_source`; otherwise report `retention: retained_ci`.
6. If a write/delete call has an ambiguous/approval/timeout outcome, reconcile the
   exact run-owned branch, CI SHA, workflow run and expected disposition before any
   retry or no-write/cleanup claim. Never start a duplicate CI run.

FAILED_CHECKS, PENDING and auth/network/global failures do not escalate. Never move
or repair the default branch.

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
