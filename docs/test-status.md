# Validation status

## Covered

- Onboarding handoff and task resume contracts.
- Managed branch validation and restoration.
- Retained branch validation and source reset.
- Workflow synthesis and matching-CI reuse.
- External YAML asset integrity and verified-synthesis fallback contracts in 0.6.4.
  The earlier embedded-template test belonged to 0.6.2 and has been superseded.
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

## Continuity and discovery follow-up — 2026-10-09

The 0.6.4 authorization gate completed Windows CI and cleanup after explicit
approval and one corrective parent follow-up. The terminal log exposed a filtered
skill-list omission followed by successful direct reads. This establishes an
observed discovery discrepancy, not a platform fix or an extension-filter cause.
State freshness was not measured against simultaneous UI observations.

The unreleased change adds offline contract regressions for decision provenance,
scope/expiry/revocation, volatile handoff reporting and bounded locator discovery.
These are instruction/package checks, not new live Gate 1/2/3 executions.

## Remaining end-to-end coverage

- Strict branch deletion and fork fallback.
- Concurrent managed runs, interrupted execution, lease conflicts, and cleanup.
- Fresh-host marketplace installation and app connection.
- Additional failure/permission-denial paths that must stop rather than seek a
  passing fallback.

Desktop GUI or hardware checks belong to the target project's own validation plan.
