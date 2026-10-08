# Validation status

## Covered

- Onboarding handoff and task resume contracts.
- Managed branch validation and restoration.
- Retained branch validation and source reset.
- Workflow synthesis and matching-CI reuse.
- Offline regression: embedded canonical template renders when auxiliary files
  are inaccessible; a fresh Cloud runtime check is still required.
- Cross-platform package validation and reproducible release artifacts.
- Marketplace, manifest, permissions, and release-gate checks.

## Live gates — 2026-10-07

1. **Real Codex Cloud E2E — PASS with reserve.** Delegated AUTO reused matching CI and
   then created a fresh managed Windows run on a new source SHA; `main` remained
   unchanged and cleanup restored the baseline.
2. **Authorization escalation — PASS.** A read-only GitHub identity returned
   `AUTHORIZATION_REQUIRED` to the parent; explicit user approval resumed the same
   run with `Tungsteno74`, completed Windows CI, and cleaned up.
3. **Local regression gate — PASS for the two target regressions.** Neither
   `setup refresh had errors` nor an invented `managed-state.md` read recurred.

These gates also exposed platform/control-plane caveats: first-turn handoff can be
missing, packaged templates can be unavailable, Codex Tasks can lag the UI, and a
write/approval result can initially contradict provider-side execution. Version
0.6.1 adds reconciliation and structured handoff guidance; platform consistency
remains outside the plugin's direct control.

## Remaining end-to-end coverage

- Strict branch deletion and fork fallback.
- Concurrent managed runs, interrupted execution, lease conflicts, and cleanup.
- Fresh-host marketplace installation and app connection.
- Additional failure/permission-denial paths that must stop rather than seek a
  passing fallback.

Desktop GUI or hardware checks belong to the target project's own validation plan.
