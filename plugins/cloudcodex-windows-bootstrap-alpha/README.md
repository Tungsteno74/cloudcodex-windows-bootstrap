# CloudCodeX Windows Bootstrap Alpha - 0.7.0-alpha.1

This is a separate, privately importable alpha plugin. It installs alongside,
and never replaces, `cloudcodex-windows-bootstrap` 0.6.7.

## Skills

- `current-cloud-windows-bootstrap-alpha-onboarding` prepares only an empty
  Current Cloud `install_script` draft when the supported host API is exposed.
- `github-actions-windows-bootstrap-alpha` is the independent validation router.
- The other four `-alpha` skills are the isolated probe and strategies.

The onboarding skill neither publishes nor approves an environment, runs CI, or
changes `startup` or `start_skill`. If the host API is unavailable, it returns
`ALPHA_INSTALL_DRAFT_BLOCKED` with the exact bundled installer as an artifact.

The package contains no credentials and never overwrites a nonempty install
script. See the onboarding skill's local contract for the precise behavior.
