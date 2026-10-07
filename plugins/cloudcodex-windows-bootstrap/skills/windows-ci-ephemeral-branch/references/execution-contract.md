# Shared execution contract — v0.6.0

This is an instruction contract, not an installed service, callback or permission
grant. The current agent reads strategy instructions as needed.

## Run context and state

Carry `run_id`, task identity, `phase`, `interaction_context`, `escalation_mode`,
`escalation_mode_source`, source repository/full SHA, execution repository,
selected authorized account, authorization scope, strategy decision, eligible
blocker, test plan, coverage/residual checks and resource ownership.

Mode precedence is:

1. explicit current-run user CONFIRM/AUTO;
2. verified resumed explicit user choice for the same run;
3. positively identified delegated/unattended execution => AUTO;
4. directly interactive execution => CONFIRM;
5. unknown interaction context => CONFIRM.

`escalation_mode_source` is one of `explicit_user`, `resumed_explicit`,
`delegated_default`, `interactive_default`, `unknown_default`. A default is not an
account preference and must not be preserved across execution surfaces merely
because it appeared in an onboarding record. Do not infer delegated execution from
Codex-task existence, DEFERRED_TO_TASK, start_skill presence, or silence alone.

A strategy run context is valid only when the bootstrap established or explicitly
resumed all security-relevant fields needed by that strategy. A strategy selected
without valid context must make no remote write and return `ROUTER_CONTEXT_REQUIRED`
or load `$github-actions-windows-bootstrap` to establish context first.

Save a small run journal outside the source working tree before remote writes when
scratch/artifact storage exists. Record ref, workflow path, source/baseline/CI SHA,
provider run id, fork ID and intended disposition. This is recovery evidence for
this run, not a global setting. If storage is unavailable, keep exact identifiers
in the result; never promise background cleanup.

Before external resources, disclose plugin/skill, repository/revision, Actions
usage, strategy, whether a branch/fork may intentionally remain and the cleanup or
retention plan. AUTO suppresses optional plugin-strategy confirmation only; it does
not suppress host/provider approvals, explicit user policy or scope boundaries.

When AUTO is active and the current task already authorizes Windows validation,
eligible strategy writes that are a necessary and disclosed part of that same task
scope do not require a second pause solely to choose a fallback. New credentials,
broader scopes, provider approvals, ambiguous destinations, policy changes and
out-of-scope destructive actions remain authorization boundaries.

## GitHub transport

Follow the [GitHub access contract](github-access.md). Carry `github_channel`,
`github_account`, `github_access_status`, `failed_operation`, `http_status`,
`error_origin` and `error_reason`; use `not_observed` rather than guesses.
The app supplies a connection boundary, not an authenticated shell. No new credentials.

## Source and CI revision stay distinct

Validate one published full source commit SHA. Dirty/unpublished changes are
excluded, never uploaded implicitly. The synthetic CI commit adds validation
infrastructure only. The Windows job checks out exact `source_revision`, never a
moving strategy ref. Never change application code/tests to improve an outcome.

A managed baseline may be an extra commit whose tree equals its source parent
exactly; it is provenance/control metadata, not application modification. The
managed CI commit may add the temporary workflow but is never merged.

## Workflow requirements

Prefer the executing strategy's own `references/windows-workflow.yml.template`,
resolved from its observed skill root. Strategy-local contracts and templates are
runtime dependencies; sibling-skill file paths are not. If the local template
cannot be read or is invalid, construct an equivalent workflow from the mandatory
invariants embedded in that strategy. Materialization alone needs no new consent
for the same authorized plan. Validate YAML, pins, commands and the complete
planned diff before any remote Git object/ref write. If verification is incomplete,
stop with `WORKFLOW_MATERIALIZATION_UNVERIFIED`. Do not use Plugin Creator/editor
tools as a runtime template dependency.

Mandatory invariants:
- only `on.push.branches` for the exact strategy branch;
- one bounded GitHub-hosted `windows-latest` job;
- `permissions: contents: read`, no secrets/OIDC/write token;
- checkout exact `source_revision` with `persist-credentials: false` and verify HEAD;
- trusted actions pinned to verified full SHAs when repo policy permits;
- only native Windows checks from the selected test plan;
- explicit native-command failure propagation and finite timeout;
- no unrelated uploads/caches/credential logging.

## Observe boundedly

Prefer host completion events. Otherwise use bounded progressive checks, not tight
polling. Return PENDING with exact run id when observation budget expires; do not
start a duplicate run or move/delete a ref while required jobs are active.
A pass requires intended Windows jobs/checks to finish successfully on exact source
SHA. Application/test failure is FAILED_CHECKS, not an escalation trigger.

## Cleanup, retention and idempotence

Only mutate/remove resources with recorded strategy ownership and unchanged expected
state. Expected-SHA leases are mandatory for managed/neutralization force updates.
Never remove/move the default branch, a user fork, unknown branch or another run's
resource. Ambiguous results require reconciliation, not blind retry.

`cleanup: complete` means the strategy reached its declared disposition. Pair it
with `retention` and `remaining_resources`:
- strict ephemeral -> `retention: none`;
- managed -> `retention: managed_baseline`;
- retained ephemeral reset to source -> `retention: retained_source`;
- retained ephemeral still at CI -> `retention: retained_ci`.

Keep terminal Actions history by default. If expected disposition cannot be reached,
report `cleanup: required`. Cleanup cannot be guaranteed after abrupt termination.

## Cross-phase continuity

`DEFERRED_TO_TASK` carries pending work, not write authorization. It also is **not a
prohibition on later writes**. A no-write statement from onboarding describes that
onboarding attempt unless an explicit user/host/repository policy prohibition was
recorded separately.

On resume, recheck source SHA, capabilities and scope. Preserve a mode only when the
record proves an explicit user choice for the verified same run. An onboarding
`interactive_default`/`unknown_default` CONFIRM is not an explicit preference and
must not freeze a later delegated task into CONFIRM. Likewise a default AUTO is not
portable to an unrelated or directly interactive task. Recompute defaults from the
actual current interaction context. DEFERRED_TO_TASK itself does not establish that
context.

Under CONFIRM, ask before the first strategy side effect that is not already
authorized. Under AUTO, route autonomously among eligible strategies within current
authorization; if authorization is missing or ambiguous return
`AUTHORIZATION_REQUIRED`, not an invented consent.

## Compact result

```text
WINDOWS_CI_BOOTSTRAP: <REUSED|COMPLETED|FAILED_CHECKS|PENDING|AWAITING_CONFIRMATION|AUTHORIZATION_REQUIRED|DEFERRED_TO_TASK|BLOCKED|DECLINED|NOT_APPLICABLE>
run_id: <id>
plugin: cloudcodex-windows-bootstrap
plugin_version: 0.6.0
phase: <onboarding|task|unknown>
INTERACTION_CONTEXT: <delegated|interactive|unknown>
ESCALATION_MODE: <CONFIRM|AUTO>
ESCALATION_MODE_SOURCE: <explicit_user|resumed_explicit|delegated_default|interactive_default|unknown_default>
skills_used: <actually loaded skill names>
github_channel: <connector|existing_git|existing_cli|mixed|none>
github_account: <verified login or not_observed; never token/link_id>
github_access_status: <read_verified|capability_missing|authorization_required|denied|unclassified|not_observed>
failed_operation: <tool/endpoint and method, or none>
http_status: <observed code or not_observed>
error_origin: <provider|host|terminal|unknown|none>
error_reason: <sanitized evidence or none>
strategy: <existing_ci|ephemeral_strict|managed_branch|fork|ephemeral_retained|none>
source_repository: <owner/repo>
source_revision: <full SHA or not_observed>
unpublished_changes: <excluded|none|not_observed>
execution_repository: <owner/repo or none>
baseline_revision: <managed baseline SHA or none>
ci_revision: <full SHA or none>
workflow_materialization: <local_template|synthesized|not_prepared>
template_read_status: <read|unavailable|invalid|not_attempted>
template_locator: <actual observed locator or none>
actions_run: <run id/URL or none>
windows_ci_validation: <passed|failed|pending|not_run>
covered_checks: <checks actually run>
residual_windows_checks: <unverified checks>
temporary_resources: <run-owned refs/fork IDs actually created>
persistent_resources: <managed/retained refs intentionally remaining, or none>
cleanup: <complete|required|pending|not_needed>
retention: <none|managed_baseline|retained_source|retained_ci|unknown>
remaining_resources: <exact IDs or none>
repository_changes: <strategy ref/workflow/object writes, or none>
default_branch_written: false
next_skill: <name/mode or none>
missing_capability: <exact tool/permission/skill or none>
handoff_status: <not_needed|returned_to_caller|persisted_by_caller|unavailable>
handoff_locator: <actual report/start-instruction reference or none>
environment_retry_required: <no|platform_decides>
```
