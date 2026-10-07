# Validation status

## Covered

- Onboarding handoff and task resume.
- Managed branch validation and restoration.
- Retained branch validation and source reset.
- Workflow synthesis and matching-CI reuse.
- Cross-platform package validation and reproducible release artifacts.
- Marketplace, manifest, permissions, and release-gate checks.

These results cover tested paths only; agent behavior still depends on host,
permissions, model execution, and provider availability.

## Remaining end-to-end coverage

- Delegated AUTO with explicit override handling.
- Strict branch deletion and fork fallback.
- Concurrent managed runs, interrupted execution, lease conflicts, and cleanup.
- Fresh-host marketplace installation and app connection.
- Failure/permission-denial paths that must stop rather than seek a passing fallback.

Desktop GUI or hardware checks belong to the target project's own validation plan.
