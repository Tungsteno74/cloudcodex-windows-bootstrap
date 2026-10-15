# Current Cloud skill installation alpha

This is an isolated, opt-in **alpha hypothesis** for the Root-to-Cloud-Child
skill propagation gap. Manual normal tasks can load plugin skills, while Root
follow-ups currently may not resolve the same packages. Copying skills onto the
environment filesystem is not a proven solution and does not guarantee that the
tool skill reader can access those local directories.

Do not change the stable `0.6.7` plugin, its manifests, `SKILL.md`, or the
environment startup script for this experiment.

## Add during environment onboarding

When an alpha revision has been reviewed and published, add this command to the
**INSTALL** script field of the existing Cloud Current environment, before its
first publish:

```bash
ALPHA_SCRIPT_SHA="<PUBLISHED_ALPHA_SCRIPT_SHA>"
alpha_checkout="$(mktemp -d)"
trap 'rm -rf -- "$alpha_checkout"' EXIT
git clone --quiet --no-checkout https://github.com/Tungsteno74/cloudcodex-windows-bootstrap.git "$alpha_checkout/repo"
git -C "$alpha_checkout/repo" checkout --quiet --detach "$ALPHA_SCRIPT_SHA"
test "$(git -C "$alpha_checkout/repo" rev-parse HEAD)" = "$ALPHA_SCRIPT_SHA"
bash "$alpha_checkout/repo/tools/install_current_cloud_skills_alpha.sh"
```

Replace `<PUBLISHED_ALPHA_SCRIPT_SHA>` with the full immutable commit SHA that
contains the reviewed alpha script. Do not use a branch, tag, mutable ref, or
`curl | bash`. The installer itself separately clones and checks out the pinned
`0.6.7` source SHA, verifies its package version, and uses no credentials.

The optional `CURRENT_CLOUD_SKILLS_ALPHA_SOURCE=/path/to/checkout` override is
only for explicit offline testing; normal onboarding must omit it so the
pinned public source is downloaded.

This belongs in onboarding only when plugin injection is missing. A normal task
published after successful onboarding remains a normal task; do not add this to
the startup script or use it to re-register the plugin.

## What it changes

The installer puts real directory copies of exactly five skill bundles under
`$HOME/.agents/skills`. It preserves their `references/` files and `.yml` YAML
assets, does not create symlinks, does not overwrite another skill, and is
idempotent only when an existing copy is byte-identical. It stages the copies
first and removes alpha copies it just installed if a later installation step
fails.

This setup is an environment filesystem snapshot. It can be absent from a
subsequently published environment or from a different user account because
`$HOME` is user- and environment-specific. It is not release-ready.

## Verify after publishing

In a manual normal task, make a read-only request to load one installed skill
and record whether it succeeds. Then issue a Root follow-up requesting the same
read-only load. Check for duplicate skill names in the surfaced inventory and
record which source was used. A successful directory copy alone is not evidence
that Root follow-ups can resolve it.

Do not perform remote writes, CI runs, plugin registration, or GitHub tool
changes for this alpha. If the reader cannot access the local copy, report that
result as a failed hypothesis rather than bypassing the reader.

## Rollback

Review the original installer output. Only lines beginning with 'installed directory copy:' identify paths created by this alpha. Do NOT delete paths logged as 'already installed and identical'.
Before cleanup, verify that each candidate is an unchanged real directory that matches the pinned original. Never remove the skills root or any unrelated/preexisting skill. Example for one folder that the installer explicitly reported creating:

```bash
skill="github-actions-windows-bootstrap"
source_skill="/path/to/pinned/0.6.7/checkout/plugins/cloudcodex-windows-bootstrap/skills/$skill"
target_skill="$HOME/.agents/skills/$skill"
test -d "$target_skill" && test ! -L "$target_skill" &&
  diff -qr "$source_skill" "$target_skill" &&
  rm -r -- "$target_skill"
```
