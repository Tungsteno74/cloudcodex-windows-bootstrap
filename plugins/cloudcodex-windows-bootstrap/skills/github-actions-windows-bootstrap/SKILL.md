---
name: github-actions-windows-bootstrap
description: >-
  Validate or resume an observed Windows-only gap for a Linux Codex Cloud
  environment. Use during environment onboarding or at the start of a normal task
  that inherits DEFERRED_TO_TASK. Reuse exact-revision CI first; otherwise route
  strict ephemeral, managed, fork or retained strategies. Explicit user mode wins;
  delegated/unattended execution prefers AUTO, interactive or unknown execution
  defaults to CONFIRM. Strategy skills require this bootstrap run context.
---

# Windows CI bootstrap — entry skill

This skill owns routing, run context and escalation policy. Strategy skills may be
selected implicitly by Codex, but their own guards must reject writes without a
valid bootstrap context. Do not resolve sibling SKILL.md files manually; invoke the
installed strategy by skill name.

## 1. Select and disclose the escalation mode

Treat one validation request for one source revision as one run. Determine the
mode in this strict precedence order:

1. An explicit current-run user choice of `CONFIRM` or `AUTO` wins.
2. A verified resumed same run may retain an **explicit** prior user choice.
3. If the current caller/host positively identifies this execution as delegated,
   unattended or single-shot with no immediate user decision loop expected, use
   `AUTO` as `delegated_default`.
4. If the user is directly interacting with this run, use `CONFIRM` as
   `interactive_default`.
5. If interaction context cannot be established, use `CONFIRM` as
   `unknown_default`.

Do **not** infer delegated execution merely because this is a Codex Cloud task,
because the run inherited `DEFERRED_TO_TASK`, because a start_skill exists, or
because no user message is currently visible. Positive evidence may come from host
or caller metadata, an explicit parent-agent/delegation instruction, or equivalent
runtime context that distinguishes delegated execution from direct user interaction.
If such evidence is absent, choose CONFIRM.

A default mode is not an explicit user preference and is never persisted account-
wide. When a run crosses from onboarding to a new task surface, recompute a default
mode from the new actual interaction context unless a verified explicit user choice
for the same resumed run must be retained.

At the start of every run print:

```text
WINDOWS_CI_RUN: <new or resumed run id>
plugin: cloudcodex-windows-bootstrap
ESCALATION_MODE: <CONFIRM|AUTO>
ESCALATION_MODE_SOURCE: <explicit_user|resumed_explicit|delegated_default|interactive_default|unknown_default>
INTERACTION_CONTEXT: <delegated|interactive|unknown>
alternative: <AUTO when CONFIRM; CONFIRM when AUTO>
```

Explain briefly that AUTO chooses among eligible plugin strategies without
widening authorization, while CONFIRM asks before optional strategy escalation.
Neither mode overrides host approvals, repository policy, permissions or user scope.

## 2. Reuse evidence and establish context

Read the [execution contract](references/execution-contract.md) and
[GitHub access contract](references/github-access.md) once per run. Reuse the
onboarding/task evidence for host OS, inspected files and Windows-only gaps; do not
repeat a full scan or deliberately run an incompatible test.

Establish a strategy run context containing at least:

- `run_id`, `phase`, source repository and full `source_revision`;
- `INTERACTION_CONTEXT`, `ESCALATION_MODE`, `ESCALATION_MODE_SOURCE`, and any
  explicit strategy choice for this same run;
- CI-capable checks, expected postconditions and residual desktop/hardware checks;
- observed GitHub account/channel/capabilities and authorization status;
- no-write/write state for this run, with explicit policy prohibitions separated
  from the mere absence of prior authorization.

Creating refs/workflows/forks and running Actions are external changes. A plugin
installation or deferred record is not authorization. Under CONFIRM, ask before the
first strategy side effect not already authorized. Under AUTO, when the task already
authorizes Windows validation and the selected strategy's disclosed writes are
within that existing scope, do not add a separate pause solely to choose among
eligible plugin strategies. AUTO is routing preference, not permission expansion:
new credentials, broader scopes, provider/host approvals, ambiguous destinations,
destructive actions outside the declared disposition, or explicit policy barriers
still require the appropriate user/provider action or return AUTHORIZATION_REQUIRED.

Conversely, a statement that onboarding created no remote writes is **not** a
prohibition on later writes unless an explicit user/host/repository prohibition was
recorded.

If no required check can run on hosted Windows, return NOT_APPLICABLE and list the
residual checks. Do not create CI merely to repeat static work.

## 3. GitHub access and existing-CI reuse

Before GitHub operations, read `references/github-access.md` once per run. Prefer
native GitHub connector operations and select the authorized account explicitly.
Do not start with terminal curl/gh probes or infer global denial from a terminal
failure.

Identify `phase: onboarding|task|unknown` from the actual caller. If initial
repository/Actions tools are absent during positively identified onboarding, use
the Phase handoff below.

Inspect only relevant existing CI. Reuse a trustworthy Windows run only when its
source repository, full source SHA, selected checks and expected postconditions
match. Verify actual job results/coverage; a branch tip or COMPLETED label alone is
insufficient.

If no reusable result exists, invoke `$windows-ci-ephemeral-branch` with the active
bootstrap context and `ephemeral_mode=ephemeral_strict`. Do not open its SKILL.md via
a sibling relative path. Strict ephemeral is always the first new-CI strategy.

## 4. REF_DELETE_UNAVAILABLE decision

When strict ephemeral returns `REF_DELETE_UNAVAILABLE` before any remote CI write,
and publication/Actions remain otherwise usable:

### CONFIRM

Return `AWAITING_CONFIRMATION` and offer:

1. **Retained branch** — invoke `$windows-ci-ephemeral-branch` with
   `ephemeral_mode=ephemeral_retained`; branch may remain.
2. **Managed branch** — invoke `$windows-ci-managed-branch`; one reusable plugin
   branch remains at a verified no-workflow baseline after terminal completion.
3. **Stop** — DECLINED with no remote writes.

State persistence/cleanup consequences. Silence is not consent.

### AUTO

Announce each transition and try, in order:

1. `$windows-ci-managed-branch`;
2. `$windows-ci-fork-fallback` only when a fork can plausibly resolve the managed
   preflight blocker;
3. `$windows-ci-ephemeral-branch` in `ephemeral_retained` mode as terminal fallback
   when the only relaxed guarantee is branch deletion.

Do not pause merely for strategy selection when AUTO was selected by explicit user
choice or `delegated_default` and the route stays within already authorized task
scope. AUTO never authorizes new credentials, policy changes, provider approvals or
out-of-scope destructive operations.

## 5. General escalation rules

Strategy skills are allowed to be implicitly selected **only inside a valid
bootstrap run context**. Their metadata being implicit-enabled does not itself grant
permission to write. If a strategy reports `ROUTER_CONTEXT_REQUIRED`, establish or
resume context here and then re-invoke it; do not fabricate context inline.

Under CONFIRM, every new fallback not already chosen by the user requires
confirmation before its first remote write. Under AUTO, announce and continue only
while eligible and within existing authorization. If authorization is missing or
ambiguous, return `AUTHORIZATION_REQUIRED`; do not downgrade AUTO into an invented
consent. Test failures, missing runtime dependencies, generic auth/network errors,
queued/PENDING runs, rate limits and global outages are NOT fallback triggers.
At most one strategy may publish a Windows CI ref and start a Windows run per run.
Once a run starts, FAILED_CHECKS and PENDING never escalate. Do not loop.

`AWAITING_CONFIRMATION` is for a real CONFIRM-mode strategy decision or an actual
interactive approval that the host/provider requires. A delegated-default AUTO run
must not emit AWAITING_CONFIRMATION merely because multiple eligible plugin
strategies exist.

**Missing skill/tool:** name it exactly. Never silently install another plugin,
invent a provider operation, or treat a missing sibling file as permission to
reimplement a different strategy.

## 6. Finish honestly

Always emit the shared result contract, including early BLOCKED,
AWAITING_CONFIRMATION, AUTHORIZATION_REQUIRED and DEFERRED_TO_TASK exits. A
successful ref write or scheduled run is not a Windows test pass. Continue permitted
Linux work while Windows is pending/blocked.

Do not edit environment install instructions, force Publish/Republish, recreate an
environment or modify AGENTS on this skill's behalf.

## 7. Phase handoff — onboarding first, task fallback

Keep attempting Windows CI during onboarding when app tools and scope allow it.
Only when all conditions hold, return `DEFERRED_TO_TASK` instead of global BLOCKED:

- phase is positively identified as environment onboarding;
- repository/full source SHA and Windows gap are known;
- initial GitHub repository/Actions tools are absent from that host with
  `error_origin: host`, `github_access_status: capability_missing`, no provider denial;
- this validation request created no remote objects, refs, forks or Windows run.

`REF_DELETE_UNAVAILABLE` still uses the normal strategy decision and a missing
optional template still uses synthesis. Provider denial, explicit prohibition,
FAILED_CHECKS, RATE_LIMITED, FORBIDDEN_UNCLASSIFIED, network failure and PENDING
are **not** reasons to defer. Unknown phase stays BLOCKED. A normal task with
missing GitHub tools stays BLOCKED; do not defer recursively.

Return a compact pending-work record with repository/full SHA, planned checks,
postconditions, residual checks, originating run id, plugin version, missing
capability, `INTERACTION_CONTEXT`, `ESCALATION_MODE` and
`ESCALATION_MODE_SOURCE`. Ask the calling onboarding agent, within its own
configuration authority, to preserve this continuation in `start_skill`:

> Windows validation is DEFERRED_TO_TASK for the recorded repository/revision and
> checks. At the start of the next normal Cloud task, use the installed
> github-actions-windows-bootstrap skill to recheck capabilities and existing CI.
> Reuse matching verified results before creating resources. Preserve only an
> explicit user mode choice for the verified same resumed run. Otherwise recompute
> the mode from the task's actual interaction context: delegated/unattended => AUTO;
> interactive or unknown => CONFIRM. This note grants no write permission, but it
> is not a prohibition on later writes; normal authorization rules apply.

Do not create the task or promise an automatic hook. Report whether persistence was
actually confirmed by the caller.

### Resume in a normal Cloud task

When a task inherits that record, resume without repeating the entire onboarding.
Recheck exact source revision, current host capabilities, user scope and existing CI.
If validation already succeeded for matching revision/coverage, return REUSED.
Failed/PENDING CI remains failed/pending and is not retried just because phase changed.

Do not carry an onboarding **default** CONFIRM/AUTO as if the user chose it. Preserve
a mode only when `ESCALATION_MODE_SOURCE` proves an explicit current-run user choice
and same-run continuity is verified. Otherwise recompute the default from the actual
new task context using section 1. `DEFERRED_TO_TASK` by itself does not prove the
new task is delegated. A changed revision/plan starts a new run. No environment
recreation is needed.
