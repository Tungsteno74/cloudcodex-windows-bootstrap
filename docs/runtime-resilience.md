# Runtime resilience and orchestration guidance

The live 0.6.x gates showed that the plugin core can complete Windows CI while the
surrounding control plane exposes delayed, missing, or contradictory state. This
document separates responsibilities and defines safe recovery.

## Observed classes

- **Parent/task handoff:** a published `start_skill` may not be visible to the first
  child turn. The parent should send repository, full source SHA, checks,
  authorization scope and delegated/interactive context explicitly.
- **Stale task reporting:** Codex Tasks output may lag the task UI. Treat the task
  connector as advisory and inspect the provider before declaring completion or
  failure.
- **Ambiguous write/approval outcome:** a write tool may report approval/failure while
  refs, commits and Actions continue asynchronously. Never equate that first response
  with a guaranteed no-op.
- **Resource mounting:** auxiliary templates can be unavailable on some Cloud hosts.
  Every strategy now embeds the canonical YAML directly in its SKILL.md; this
  deterministic fallback precedes guarded synthesis and does not repair the
  platform's resource mount itself.
- **Agent path drift:** no `managed-state.md` resource exists. Managed state is the
  provider ref/marker history plus the run journal.

## Safe recovery protocol

1. Preserve the same task and `run_id`; do not create another run by default.
2. Reconcile authoritative provider state using the exact repository, source SHA,
   expected branch/workflow, marker commits and Actions run identifiers.
3. Resume observation/cleanup when work exists. Retry once only after absence is
   confirmed and authorization is still valid.
4. Stop without retry when provider state is inconclusive, reporting exact remaining
   resources and cleanup risk.
5. Parent orchestrators should inject compact context on the first delegated turn and
   use external reconciliation as a safety net; this does not replace plugin-side
   reconciliation.

## Layer ownership

- **Plugin/Codex instructions:** avoid invented paths, reconcile ambiguous writes,
  produce structured context requests, and never duplicate CI from stale status.
- **Root orchestrator:** pass explicit delegation context, compare executor reports
  with persistent provider state, and resume the same run.
- **Platform/control plane:** ultimately owns consistent task events, approval state,
  environment binding and resource mounting.
