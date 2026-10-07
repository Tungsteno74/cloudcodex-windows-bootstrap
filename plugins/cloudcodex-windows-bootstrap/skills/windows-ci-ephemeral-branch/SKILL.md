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
Resolve against this skill's observed root, never against repository cwd or a
sibling skill. Do not invent plugin IDs, URI schemes or mount paths. Do not require
Plugin Creator or archive-editor access at runtime.

If the local template is missing/unreadable/invalid, set
`workflow_materialization: synthesized` and construct an equivalent workflow with
all mandatory invariants:
- exact literal `on.push.branches` for this strategy branch only;
- one bounded `windows-latest` job, default shell `pwsh`;
- `permissions: contents: read`, no secrets/OIDC/write token/self-hosted runner;
- checkout exact `source_revision`, `persist-credentials: false`, verify HEAD;
- trusted actions pinned to verified full SHAs, no moving tags;
- only approved native Windows checks/setup;
- `$ErrorActionPreference = 'Stop'` and explicit native failure propagation;
- parse YAML, resolve placeholders and review the complete CI-only diff before any
  remote Git object/ref write.

If an invariant cannot be verified, return `WORKFLOW_MATERIALIZATION_UNVERIFIED`.
Materialization is not a new strategy/escalation and does not alter permissions.

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

FAILED_CHECKS, PENDING and auth/network/global failures do not escalate. Never move
or repair the default branch.
