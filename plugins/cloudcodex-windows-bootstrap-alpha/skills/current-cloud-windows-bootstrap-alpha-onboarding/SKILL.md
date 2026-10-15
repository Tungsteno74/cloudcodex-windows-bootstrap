---
name: current-cloud-windows-bootstrap-alpha-onboarding
description: >-
  Prepare the exact bundled alpha installer in an empty Cloud Current environment
  install_script draft only when the supported draft API is exposed and alpha was
  explicitly requested. Never publish, approve, run CI, alter startup/start_skill,
  or overwrite a nonempty install script.
---

# Current Cloud Windows Bootstrap Alpha onboarding

This is an independent alpha onboarding path, not a production-skill bridge.
Use it only when the caller explicitly requested the Alpha package and the actual
environment is Cloud Current. It does not establish plugin availability in a later
normal Cloud task: publishing and task-time skill discovery are host-controlled.

Read the bundled [onboarding contract](references/onboarding-contract.md) before
any environment call. The exact installer is [the local asset](assets/install_current_cloud_skills_alpha.sh);
use its bytes as the requested artifact or `install_script` value. Do not depend
on a caller filesystem path when the environment later executes the script.

## Guarded procedure

1. Detect whether the onboarding host exposes an actual supported Current Cloud
   draft read/update capability, for example
   `cloud_environment_onboarding_update_environment_config_draft`. Native skill
   reader tooling is preferred for local resources; filesystem fallback is only a
   local-resource fallback, never proof that a post-publish task can load a skill.
2. If no supported capability exists, this skill cannot run in onboarding, the
   environment is not verified Cloud Current, or Alpha was not explicitly requested,
   return `ALPHA_INSTALL_DRAFT_BLOCKED` and attach/report the exact asset bytes.
   Do not claim a write succeeded or speculate that Root follow-ups will fix it.
3. Read the current draft. Preserve `startup` and `start_skill` exactly. If
   `install_script` is nonempty and differs from the exact asset, return
   `ALPHA_INSTALL_DRAFT_MERGE_NEEDED`; do not mutate it. If it is already exactly
   equal, return `ALPHA_INSTALL_DRAFT_PRESENT` without a write.
4. Only when `install_script` is empty, apply the schema exposed at runtime and
   update **only** that field with the exact asset content. Read back the draft
   when supported, and report the observed result. Never publish, approve, create
   CI, alter plugin registration, bypass authorization, or handle user secrets.

Report `ALPHA_INSTALL_DRAFT_APPLIED` only after the update call returns success and
the supported read-back confirms the exact script. Otherwise return the precise
blocked or uncertain outcome with the asset artifact.
