---
name: windows-ci-fork-fallback
description: >-
  Fork fallback for an active github-actions-windows-bootstrap run when a recorded
  source-side preflight blocker can plausibly be resolved in an authorized fork.
  Requires the same run's CONFIRM approval or AUTO routing plus a complete cleanup
  plan. May be selected implicitly only with valid bootstrap context.
---

# Windows CI — fork fallback

Read this skill's local [execution contract](references/execution-contract.md),
[GitHub access contract](references/github-access.md), and
[provider constraints](references/github-constraints.md). Do not depend on sibling
skill files.

## Router-context guard

Require valid bootstrap run context with repository/full source SHA, eligible
preflight blocker, CONFIRM/AUTO routing, test plan/postconditions, account/channel
and authorization state. Without it make no remote write; invoke
`$github-actions-windows-bootstrap` or return `ROUTER_CONTEXT_REQUIRED`. Implicit
availability never authorizes fork creation.

## Minimum permission and cleanup plan

Discover actual fork creation, workflow publication, Actions observation and
cleanup capabilities before creating resources. Source read access is necessary
but insufficient. Verify provider policy permits destination and preserve private
visibility. Never switch accounts by connection order, create new tokens, enlarge
scopes or copy private source to public storage.

A fork is useful only with an independent safe cleanup/persistence route: ref
removal, managed reset in an authorized existing fork, or deletion of a newly
created run-owned fork when explicitly authorized/callable after evidence export.
If none exists return `FORK_CLEANUP_UNAVAILABLE`. Pre-existing user forks are never
deleted.

## Local workflow materialization

Prefer [local workflow template](references/windows-workflow.yml.template) from this
skill root. Never read a sibling template or require Plugin Creator at runtime.
If unavailable/invalid, synthesize an equivalent workflow only when mandatory
invariants are verifiable: exact branch trigger; bounded `windows-latest`/pwsh job;
contents-read only; exact source checkout with `persist-credentials: false` and
HEAD assertion; verified full-SHA actions; approved Windows checks; explicit failure
propagation; YAML/pin/diff validation before remote writes. Otherwise return
`WORKFLOW_MATERIALIZATION_UNVERIFIED`.

## Execute

1. Resolve/announce exact fork owner/repository/source SHA. Materialize and validate
   the workflow before fork resources. Ambiguous destination => stop.
2. If creating a fork, use unique run-owned destination and record repository ID;
   reconcile uncertain responses before retrying.
3. Inspect fork Actions/inherited automation before enabling or writing. Do not
   weaken policy or enable privileged/scheduled behavior unexpectedly.
4. Execute CI **inside the fork only** using the predeclared strict or managed
   branch procedure compatible with the cleanup plan. Do not recurse through the
   router and do not reload a sibling template. Revalidate branch/source/execution
   repository before publication. Never inject an upstream PAT.
5. Use push-triggered CI in the fork. Do not open a PR, merge, or write the source default branch; do not rely on upstream PR Actions.
6. Collect exact Windows results then execute the predeclared cleanup/disposition.

Leave pre-existing forks untouched except exact run-owned refs/baselines authorized
by the strategy. FAILED_CHECKS, PENDING or post-write cleanup problems do not fall
through to another execution strategy. A preflight-only fork blocker may return to
the bootstrap router for terminal retained consideration when still eligible.
