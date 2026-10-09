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
- **Resource loading:** auxiliary assets may be unreadable on some hosts;
  prefer registered YAML resources and preserve guarded, independently verified
  workflow synthesis only when strategy invariants are known.
- **Discovery completeness:** a filtered skill inventory can omit loadable
  strategies. After name dispatch and bounded trusted-locator reads, a strategy
  may be reconstructed only for the same run from independently verified
  authoritative requirements. Otherwise return BLOCKED to the Root.
  Inventory omissions and resource-read failures are separate classes.
- **Decision continuity:** confirmed same-scope choices should survive a resume;
  technical permissions, remembered defaults and previous success are not grants.
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

## Decision continuity and guarded strategy recovery

Use the existing journal/handoff to carry decisions, their authority and validity;
revalidate changed conditions without resetting every decision or asking for the
same still-valid consent. Run-scoped authorization cannot silently become project-
scoped authorization. Never persist secrets. A temporary file is not durable storage.

Try the installed strategy normally, then a bounded read of a known, same-release
locator through a supported host interface. If still unavailable without denial,
reconstruct only a fully verified run-local plan for the same strategy; otherwise
return BLOCKED or AUTHORIZATION_REQUIRED to the Root. Listing, resource reading
and provider operations are distinct.
The entry skill and shared contracts define the plugin-specific path; general
Root/Child policies belong in their existing orchestration instruction sources.

Control-plane state freshness cannot be established from task completion alone.
Compare simultaneous task, provider and UI observations before claiming a fix.
Instruction changes do not repair event delivery, authority indexing or runtime
caches. Offline tests verify contracts and packaging, not autonomous host behavior.
