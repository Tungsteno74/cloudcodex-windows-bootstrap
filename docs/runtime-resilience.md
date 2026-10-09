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
- **Resource loading:** the former `.template` assets were not readable through the
  tested loader. Version 0.6.4 uses external `assets/windows-workflow.yml`; the
  version 0.6.2 embedded fallback is historical and has been removed.
- **Discovery completeness:** a later 0.6.4 gate omitted strategy names from a
  filtered inventory while direct skill-locator reads succeeded. An empty list
  therefore did not establish unavailability in that run. It does not prove a
  causal connection to the former extension filter or to any Cloud generation.
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

## Targeted continuity and discovery hardening — unreleased

Use the existing journal/handoff to carry decisions, their authority and validity;
revalidate changed conditions without resetting every decision or asking for the
same still-valid consent. Run-scoped authorization cannot silently become project-
scoped authorization. Never persist secrets. A temporary file is not durable storage.

Try the installed strategy normally, then a bounded read of a known, same-release
locator through a supported host interface. Check identity/version before use;
stop on denial. Listing, resource reading and provider operations are distinct.
The entry skill and shared contracts define the plugin-specific path; general
Root/Child policies belong in their existing orchestration instruction sources.

The stale-task issue was not reproduced in the completed gate; it is not proven
fixed. This change does not repair event delivery, authority indexing or runtime
caches. Legacy/current Cloud comparisons and live autonomous behavior under these
new instructions remain unverified. Offline contract tests check the published
instructions and packaging, not execution by a live agent.
