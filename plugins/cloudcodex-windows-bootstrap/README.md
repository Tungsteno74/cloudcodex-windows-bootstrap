# CloudCodeX Windows Bootstrap - 0.6.0

Multi-skill Windows validation for Codex Cloud through GitHub Actions. The plugin
requires the configured GitHub app and ships no credentials, MCP server, or Windows
service.

## Skills

- `github-actions-windows-bootstrap` - entry router, run context, and handoff.
- `windows-ci-ephemeral-branch` - strict or retained temporary branch.
- `windows-ci-managed-branch` - reusable managed branch with a clean baseline.
- `windows-ci-fork-fallback` - optional fork strategy when eligible.
- `codex-cloud-windows-check-probe` - explicit diagnostic probe.

The four operational skills allow implicit invocation. Strategy skills still require
a valid bootstrap context before remote writes.

## Escalation

Mode precedence:

```text
explicit user choice        -> wins
resumed explicit choice     -> preserved for the same run
delegated/unattended run    -> AUTO
interactive run             -> CONFIRM
unknown context             -> CONFIRM
```

AUTO selects among already eligible strategies; it does not authorize new
credentials, broader scopes, provider approvals, or policy exceptions.

## Strategy flow

```text
matching existing CI
   -> strict ephemeral
      -> managed
      -> eligible fork
      -> retained ephemeral
```

A failed or pending Windows run does not trigger strategy hopping. Normal plugin
operation never merges or writes the target repository's default branch.

## Onboarding handoff

When GitHub repository/Actions tools are unavailable during positively identified
onboarding, the bootstrap can return `DEFERRED_TO_TASK`. A later normal task may
resume the recorded validation after rechecking source revision, capabilities,
authorization, and existing CI.

The handoff carries pending work, not write permission, and is not a guaranteed
platform hook.

## Package resources

Each strategy contains local copies of its execution contract, GitHub constraints,
and workflow template. The bootstrap reference directory is the authoring source;
the synchronization tools keep strategy copies aligned.

If a workflow template cannot be read at runtime, the strategy may synthesize an
equivalent workflow from the same mandatory invariants and validate it before any
remote write.

See the repository documentation for installation, release status, and remaining
end-to-end coverage. Licensed under MIT.
