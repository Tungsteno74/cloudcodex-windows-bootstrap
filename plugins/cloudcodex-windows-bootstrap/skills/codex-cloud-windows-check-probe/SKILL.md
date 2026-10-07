---
name: codex-cloud-windows-check-probe
description: >-
  Explicit read-only diagnostic for a Windows validation gap already observed by
  Codex Cloud onboarding. Use only when the user or another instruction explicitly
  asks to run the probe. Do not invoke implicitly when the
  github-actions-windows-bootstrap skill is available.
---

# Windows check probe

This retained diagnostic verifies that plugin skill loading works. It does not
supply a Windows runner or remediate compatibility.

## Procedure

1. Reuse the already observed host OS, revision and Windows-only validation gap.
2. Read `references/probe-marker.txt` from this skill root.
3. Emit the established `WINDOWS_CHECK_PROBE` report.
4. Make no repository, Git, environment, credential, workflow, or external changes.

Do not use this probe as the remediation path during normal Cloud onboarding.
Use `github-actions-windows-bootstrap` for that purpose.
