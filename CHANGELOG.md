# Changelog

## Unreleased

- Reuse verified decision/authorization context within its still-valid scope;
  record provenance, revocation and actual journal durability without storing secrets.
- Recover installed skills omitted from filtered lists through bounded, verified
  locator reads; preserve version, authority, router and provider permission guards.
- Distinguish push-triggered Actions scheduling from optional dispatch APIs.
- Keep stale-task reporting and Legacy Cloud hypotheses separate from these fixes.
- Recover the same strategy locally only from independently verified safeguards,
  otherwise return an explicit BLOCKED/authorization handoff to the Root.

## 0.6.4 ? 2026-10-08

- Move the canonical workflow template to `assets/windows-workflow.yml`
  and distribute synchronized copies inside each strategy.
- Fix Cloud resource-loading compatibility: `.yaml` and `.yml`
  are readable, while the former `.yml.template` suffix is not registered.
  Confirmed with identical-byte probes in both skill directories.
- Remove duplicated embedded YAML from SKILL.md; preserve verified synthesis
  as an exceptional fallback with existing security/authorization guards.

## 0.6.2 — 2026-10-08

- Embed a verified copy of the Windows workflow template in each strategy SKILL.md so Cloud agents can materialize it without auxiliary resource mounts. Synchronize and test the inline/sidecar copies at build time.

## 0.6.1 — 2026-10-07

- Reconcile ambiguous approval/tool outcomes against provider refs, marker commits, and Actions runs before retry or terminal reporting.
- Return structured missing handoff context to the parent and treat `start_skill` as an optimization rather than the sole continuation copy.
- Treat generic setup-refresh warnings as diagnostic, not global failure, when concrete plugin resources remain available.
- Make managed state explicitly provider-backed and forbid invented `managed-state.md` dependencies.
- Add regression coverage and document live Cloud/Local gate results and control-plane caveats.

## 0.6.0 — 2026-10-07

- Establish CloudCodeX Windows Bootstrap as the baseline public GitHub distribution.
- Provide context-aware Windows validation through existing CI, strict ephemeral, managed, eligible fork, and retained fallback strategies.
- Preserve explicit user mode precedence, delegated/unattended AUTO, interactive/unknown CONFIRM, and strict authorization boundaries.
- Ship deterministic standalone packaging, GitHub app binding, plugin branding, cross-platform validation, and release provenance.
- Keep normal operation free of automatic pull requests, merges, and default-branch writes.
