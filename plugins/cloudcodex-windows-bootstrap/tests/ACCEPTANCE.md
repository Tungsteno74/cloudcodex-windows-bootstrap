# Acceptance scenarios

End-to-end Cloud cases; package unit tests do not prove model dispatch or caller-context detection.

| Case | Expected |
| --- | --- |
| Explicit user says CONFIRM | CONFIRM wins regardless of delegated/interactive context. |
| Explicit user says AUTO | AUTO wins within current authorization boundaries. |
| Positively identified delegated/unattended task, no explicit mode | AUTO + `delegated_default`; no pause solely for strategy choice. |
| Direct interactive task, no explicit mode | CONFIRM + `interactive_default`. |
| Interaction context unavailable | CONFIRM + `unknown_default`. |
| Merely being a Codex Cloud task | Does not by itself imply delegated AUTO. |
| DEFERRED_TO_TASK inherited | Resume Windows validation; recompute default mode from actual task context unless same-run explicit user choice is verified. |
| Parent delegation is positive but handoff fields are missing | BLOCKED/returned_to_caller with exact missing repository/SHA/checks/authorization/context; no vague prompt and no writes. |
| Generic `setup refresh had errors` warning but concrete skill/resources are readable | Continue; do not recreate/republish the environment solely for the warning. |
| Cloud reads `assets/windows-workflow.yml` | Validate the external YAML and report `local_template`. |
| Cloud cannot load an asset | Independently verify every workflow invariant before synthesized fallback, otherwise stop without remote writes. |
| Write/approval result is ambiguous or task state is stale | Reconcile exact provider refs/commits/runs before retry or terminal no-write reporting; preserve the same run_id. |
| Managed strategy state lookup | Use provider ref/marker + run journal; never require `managed-state.md`. |
| Delegated AUTO reaches action outside current authorization | AUTHORIZATION_REQUIRED/provider approval; no invented consent. |
| Onboarding lacks GitHub tools | DEFERRED_TO_TASK; plan persisted by caller; no remote write. |
| Bootstrap needs strict strategy | `$windows-ci-ephemeral-branch` selected without manual user skill prompt. |
| Strategy selected without bootstrap context | ROUTER_CONTEXT_REQUIRED; no remote write. |
| delete_ref absent under CONFIRM | retained / managed / stop offered. |
| delete_ref absent under delegated AUTO | managed → eligible fork → retained terminal, without strategy-choice pause. |
| Managed existing pass matches repo/SHA/checks | REUSED; no new remote write. |
| Test fails or run pending | No fallback hopping. |
| main/default branch | Never written/merged by normal plugin flow. |

Primary live gates:
1. Directly open a task and issue a neutral prompt: expect CONFIRM unless the host explicitly marks it delegated.
2. Have Chat/another agent create a single-shot Codex task without specifying a mode: when delegation is positively exposed to the child, expect `AUTO` / `delegated_default` and no AWAITING_CONFIRMATION solely for the internal fallback choice.
3. Repeat with explicit CONFIRM and verify that explicit user choice overrides delegated default.

## Targeted continuity/discovery acceptance scenarios (live execution pending)

| Scenario | Expected behavior |
|---|---|
| Same run, explicit grant valid, new turn | Reuse the decision after revalidation; no duplicate consent prompt. |
| New run, previous grant was run-only | Do not transfer authorization; return the missing authorization. |
| Broader explicit grant covers next run | Reuse only with parent-carried provenance and matching scope. |
| Revocation, expiry or narrowed instructions | Invalidate affected decisions; no unauthorized write. |
| Multiple technical accounts, one selected valid grant | Preserve that identity; do not infer new consent from permissions. |
| Journal only in temporary storage | Report volatile; return minimum verified context for handoff. |
| Strategy omitted from filtered listing, known same-release locator readable | Load through supported reader and verify identity/version before proceeding. |
| Direct reader reports a denial | Stop; do not search for a permission bypass. |
| Locator resolves stale or different instructions | At most one supported refresh; never silently substitute versions. |
| Package-editor read succeeds but installed strategy is unavailable | Diagnostic evidence only; no substitute for an unrelated or stale skill. |
| Strategy is unreadable; same-run authoritative invariants are verified | Reconstruct the *same* router-selected run-local plan with provenance; no invented strategy. |
| Unknown marker, ownership, lease, ref deletion, fork cleanup or workflow guard | BLOCKED to Root with missing evidence, no writes. |
| Reconstructed plan lacks consent | AUTHORIZATION_REQUIRED to Root without privilege expansion. |
| Denied skill access or version mismatch | Do not reconstruct or bypass; report verified blocker. |
| Optional YAML asset unavailable, required strategy loaded | Existing independently verified synthesis remains a last resort. |
| No dispatch endpoint, verified push trigger and observation route present | Use authorized publication; observe actual jobs before reporting a pass. |
