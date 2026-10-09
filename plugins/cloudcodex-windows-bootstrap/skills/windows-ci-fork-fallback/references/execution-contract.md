# Shared execution contract — v0.6.5

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
in the result; never promise background cleanup. Provider refs, commits, repository
metadata and workflow runs are authoritative for remote effects; task/UI/connector
status is advisory and may lag.

Before external resources, disclose plugin/skill, repository/revision, Actions
usage, strategy, whether a branch/fork may intentionally remain and the cleanup or
retention plan. AUTO suppresses optional plugin-strategy confirmation only; it does
not suppress host/provider approvals, explicit user policy or scope boundaries.

When AUTO is active and the current task already authorizes Windows validation,
eligible strategy writes that are a necessary and disclosed part of that same task
scope do not require a second pause solely to choose a fallback. New credentials,
broader scopes, provider approvals, ambiguous destinations, policy changes and
out-of-scope destructive actions remain authorization boundaries.

### Decision continuity

Use the existing run journal and caller-returned handoff as the decision record;
do not introduce a service, global authorization cache or credential store. Update
it after a decision or authorization change, and before a handoff or remote write,
even when the run currently has no remote resources. Record only the decision,
verifiable user/parent grant reference, scope, validity conditions, expiry if any,
and revocation or supersession. Never record secret values or authentication headers.

On resume, revalidate the relevant conditions: acting identity and channel, source
and execution repositories, revision/check plan where covered by the grant,
permitted operations, resource disposition, current instructions and provider
permissions. Reuse a still-valid recorded decision without asking for the same
consent again. A new turn, phase or task does not itself revoke or enlarge a grant.
Run-only grants never carry into another run. A broader grant may cover a new run
only when its explicit scope does so and the parent carries verifiable provenance.
A remembered preference, repository ownership, silence or technical push permission
is not consent. An unverified record is evidence to reconcile, not permission.

Apply current restrictions and explicit revocation, expiry or supersession before
reuse. Invalidate only affected decisions; do not erase other valid choices. A new
explicit grant can resolve a previously recorded authorization gap within its scope.
Provider approvals remain independent and must not be bypassed. A changed revision
or check plan still starts a new validation run; earlier CI cannot be reused merely
because the account choice remains valid. Do not transfer credentials between
channels, users, devices or environments.

Reuse only storage already available and authorized for the task. Keep the record
outside source commits and export the minimum verified decision context in the
handoff/result when the next surface cannot read it. Report actual durability:
`volatile` for temporary files, `durable` only when persistence was confirmed, and
`result_only` when only the returned record is available. Missing persistence alone
does not revoke a grant still verifiable from the current caller context. If the
authorization evidence itself is missing, return the exact missing fields without
writes. This does not persist an inferred CONFIRM/AUTO default as an explicit choice.

## Installed skill discovery

An inventory, including authority-filtered `skills.list`, is a discovery hint, not
proof of absence or a permission grant. Prefer normal installed-skill selection by
name. If an expected strategy is omitted or name dispatch cannot locate it:

1. Obtain its locator from installed metadata or caller evidence for the same plugin
   and release. Do not guess URI schemes, identifiers or sibling filesystem paths.
   Respect host authority/scope restrictions; a missing listing is not permission to
   read another installation or broaden access.
2. Use an actually exposed skill/resource reader whose schema accepts that locator.
   Make one targeted read per supported route; at most one native metadata refresh
   is allowed when there is evidence of stale metadata. Stop at the first verified
   success, an access denial or exhaustion of these bounded checks. Do not turn a
   denial into a search for an alternative authorization route.
3. Verify plugin identity, release and strategy name against the active run before
   using the instructions. A readable matching SKILL.md loads the strategy; it need
   not expose a separate callable function. Preserve router-context guards. On
   version mismatch, never silently substitute old instructions or a different
   plugin. Report the observed mismatch if native refresh cannot resolve it.
4. Distinguish `loaded`, `loaded_by_locator`, `unlisted_unresolved`,
   `resource_unavailable`, `reader_unavailable`, `version_mismatch` and `denied`.
   Preserve the method and observed result in the journal/result. If no trustworthy
   locator or reader exists, report that specific limitation without inventing it.

Package-editor reads or public repository copies may diagnose publication but do
not substitute for loading the installed strategy. Plugin Creator is not a runtime
dependency. A missing optional YAML asset is separate from missing required strategy
instructions: existing verified workflow synthesis remains available only after the
strategy instructions and mandatory invariants are known.

## Guarded same-strategy reconstruction — exceptional last resort

If the installed strategy remains unreadable after bounded name/locator discovery
without an explicit denial, authority restriction or version/identity mismatch,
the active bootstrap may reconstruct a *run-local plan for the same routed
strategy*. This does not install or rewrite a skill, invent a strategy, or grant
authorization. A temporary diagnostic constraint from one gate is not permanent
runtime policy.

Before any external write:

1. The bootstrap, shared contracts, active run context and normal routing must
   remain available and valid. Preserve the strict-first and CONFIRM/AUTO rules.
2. Establish all target-strategy invariants from the already loaded authoritative
   context, verified release-specific metadata or independently verified provider
   evidence. A strategy name, undocumented guess, untrusted repository copy or
   previous unrelated success is insufficient.
3. Validate identity and exact source/CI SHA, permissions, run ownership,
   workflow-only diff, SHA-pinned actions, trigger, observation, concurrency,
   retention, cleanup and idempotent reconciliation before changing provider state.
4. If any required safeguard cannot be independently established, return
   `BLOCKED` with `handoff_status: returned_to_caller`, exact missing
   invariants and no remote writes; explicitly escalate to the Root. When user
   authorization is insufficient, return `AUTHORIZATION_REQUIRED` to Root.
   Access denial and identity/version mismatch never authorize reconstruction.
5. Only a verified *same-strategy* plan may execute. Report
   `strategy_materialization: reconstructed` with source and verification
   evidence. Do not claim a missing skill was loaded or create plugin files.

Minimum strategy-specific guarantees, additional to shared invariants:

- **Ephemeral strict:** verified authorized `delete_ref` before publication,
  safe push-automation preflight, unique collision-checked branch
  `codex/windows-ci/<run-id>`, CI-only workflow against pinned source SHA,
  one correlated Windows run, and deletion only of the unchanged run-owned CI
  branch after the run is terminal. Cleanup failure is `cleanup: required`.
- **Ephemeral retained:** only an explicit CONFIRM selection or terminal AUTO
  route can relax deletion. Disclose persistence before write; when permitted,
  restore the owned CI ref to the source SHA with an expected-SHA lease, or report
  the retained CI tip accurately.
- **Managed branch:** require `codex/windows-ci-managed` and
  `.github/workflows/codex-windows-ci-managed.yml`, validated ownership
  markers `cloudcodex-windows-bootstrap managed baseline v1` and
  `cloudcodex-windows-bootstrap managed ci v1`; an existing baseline must
  have exactly one parent and an identical tree. Verify no active/conflicting
  run, owned workflow path, safe publication/restoration automation and forced
  `expected_sha` lease capability. Create the no-diff source-parent baseline
  and a CI-workflow-only child commit, observe the exact Windows job, restore
  CI to baseline with lease, then read back. Unknown marker/tip blocks.
- **Fork fallback:** require a router-eligible source-side blocker, explicitly
  authorized fork destination with preserved visibility, creation/Actions
  capabilities and a complete separately authorized cleanup/retention plan.
  Never infer fork permissions, create unrelated forks or weaken visibility.

Missing `delete_ref` blocks strict ephemeral but not independently eligible
managed execution. Exceptional YAML synthesis is a separate fallback, allowed only
when all strategy and workflow invariants can be independently verified.
Never silently invent a *different* strategy, bypass denied access or infer consent.

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

Load the executing strategy's own asset at assets/windows-workflow.yml
through its registered skill resource, or through its observed skill root.
This is an independent strategy-local file: never depend on sibling skill
paths, repository cwd, or plugin editor tools. Validate the YAML, verified
substitutions, SHA pins, selected checks and complete CI-only diff before
any remote Git object/ref write.

If the asset cannot be loaded or is invalid, the strategy may synthesize an
equivalent workflow as a last resort, using only the mandatory invariants.
Do not report a successful asset read when a fallback was used. Report
workflow_materialization: synthesized and the actual template_read_status.
If full verification is impossible, return
WORKFLOW_MATERIALIZATION_UNVERIFIED without remote writes. The fallback
does not change permissions, approval requirements or the task scope.

Mandatory invariants:
- only on.push.branches for the exact strategy branch;
- one bounded GitHub-hosted windows-latest job;
- permissions: contents: read, no secrets/OIDC/write token;
- checkout exact source_revision with persist-credentials: false and verify HEAD;
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

## Ambiguous control-plane outcomes and reconciliation

A write-capable tool timeout, cancellation, approval transition, stale connector
state, or generic failure is not proof that no provider side effect occurred. Treat
the outcome as unknown unless the provider guarantees an atomic no-op. Before retry,
fallback, cleanup claims, or a terminal `BLOCKED`/`AUTHORIZATION_REQUIRED` result:

1. Preserve the same `run_id`, source SHA, account/channel and expected identifiers.
2. Perform bounded read-only reconciliation against the provider: exact refs/tips,
   marker commits and parents/trees, workflow path, branch + CI SHA runs/jobs, and
   known run-owned forks. Prefer completion events; otherwise use progressive limited
   checks and stop as soon as the state is conclusive.
3. Classify `reconciliation_status` as `confirmed_absent`, `confirmed_present`,
   `in_progress`, `terminal`, or `inconclusive`. Absence is confirmable only when all
   possible effects of that operation are observable or the provider guarantees an
   atomic no-op. If a create-object call could leave an unreferenced object and no
   object ID/SHA was returned, classify it as `inconclusive`, not `confirmed_absent`.
4. `confirmed_absent` permits at most one idempotent retry of the same operation when
   it remains authorized. `confirmed_present`/`in_progress` resumes observation or
   cleanup without duplicate writes. `terminal` reports the actual provider result.
   `inconclusive` stops without retry and reports exact uncertainty plus any cleanup
   risk.

Never claim no remote writes or `cleanup: complete` after an ambiguous outcome unless
provider read-back supports it. Never start a second strategy or run solely because
the control plane or task connector is stale.

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
recorded separately. Because `start_skill` or task metadata can be missing/stale, a
parent delegation should include the compact continuation in its first turn. If
security-relevant context is still missing, return the exact missing fields to the
parent without writes rather than guessing.

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
plugin_version: 0.6.5
phase: <onboarding|task|unknown>
INTERACTION_CONTEXT: <delegated|interactive|unknown>
ESCALATION_MODE: <CONFIRM|AUTO>
ESCALATION_MODE_SOURCE: <explicit_user|resumed_explicit|delegated_default|interactive_default|unknown_default>
skills_used: <actually loaded skill names>
skill_discovery_status: <loaded|loaded_by_locator|unlisted_unresolved|resource_unavailable|reader_unavailable|version_mismatch|denied|not_attempted>
skill_discovery_evidence: <supported reader, observed locator/version and sanitized result; or none>
strategy_materialization: <installed|loaded_by_locator|reconstructed|not_prepared>
strategy_reconstruction_evidence: <verified invariant sources and route; or none>
decision_context_status: <reused|updated|missing|invalidated|not_needed>
decision_context_locator: <actual journal or caller-returned record reference; or none>
decision_context_durability: <volatile|durable|result_only|unavailable>
authorization_origin: <verifiable current user/parent grant reference; or none>
authorization_scope: <covered identities, destinations, operations, conditions and validity; or none>
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
reconciliation_status: <not_needed|confirmed_absent|confirmed_present|in_progress|terminal|inconclusive>
reconciliation_evidence: <exact refs/run IDs/commit SHAs or none>
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
