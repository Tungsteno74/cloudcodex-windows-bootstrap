# Current Cloud skill installation alpha

`cloudcodex-windows-bootstrap-alpha` is a distinct, private-importable package.
Install it side-by-side with stable `cloudcodex-windows-bootstrap` 0.6.7; it does
not replace the stable manifest, skills, startup configuration, or plugin identity.

## Integrated onboarding path

The alpha package ships
`current-cloud-windows-bootstrap-alpha-onboarding`. During an actual Cloud Current
onboarding flow, that skill can automatically prepare the exact bundled
`install_current_cloud_skills_alpha.sh` as the environment `install_script` only
when all of the following are true:

- Alpha was explicitly requested;
- the host exposes a supported environment-draft read/update API; and
- the current draft's `install_script` is empty.

It reads the draft first, preserves `startup` and `start_skill` exactly, and writes
only `install_script`. It never publishes, approves, runs CI, creates an
environment, or overwrites a nonempty script. An existing different script produces
`ALPHA_INSTALL_DRAFT_MERGE_NEEDED` for a human merge decision.

If the draft API is unavailable or the skill cannot run during onboarding, the skill
returns `ALPHA_INSTALL_DRAFT_BLOCKED` and supplies the exact installer asset. This
does not assert client-side native injection, nor does it guarantee that a later
Root follow-up or normal Cloud task can load the plugin skills after publishing.
Native skill-resource reading is preferred; filesystem reading is only a fallback
to obtain the local asset, not evidence of normal-task availability.

## Manual fallback

When the host API is absent, an authorized operator may paste the exact asset from
the alpha package into the **install_script** draft field and review it before
publishing. Do not add it to startup, start_skill, shell profiles, or a mutable
repository download command. The asset is self-contained at install execution time
and does not rely on a caller's on-disk skill-resource path.

The installer remains an experimental filesystem snapshot. After publish, verify
skill discovery separately in a normal task. A copied directory does not prove that
the platform's skill reader, a delegated child, or a Root follow-up can resolve it.

## Safety

No user secrets, credentials, or authentication bypass are needed. Do not publish,
approve, create CI, register a plugin, or change GitHub configuration as part of
this alpha packaging or onboarding preparation.
