# Provider constraints

Use the local GitHub access contract. Native connector first; existing authenticated
Git/gh transport is a capability fallback, not a default. Never infer CLI auth from
connector read or export connector tokens.

1. Push-triggered workflow may run from the pushed branch revision; it need not be
   merged to default. Branch/ruleset/Actions restrictions still apply.
2. Repository access and token/app scopes differ. Runtime `GITHUB_TOKEN` remains
   read-only here and is not the writer credential.
3. Pushes made by a workflow's own GITHUB_TOKEN normally do not launch another
   push workflow; use only the authorized external connector/Git channel.
4. Managed branch publication/restoration are push-like ref updates. Use expected-SHA
   lease semantics and never force an unknown branch.
5. Retained branch reset to source removes the workflow from its tip but does not
   delete the ref or audit/history; report the distinction.
6. Fork creation/Actions/cleanup are separate capabilities and organization policy
   may prohibit them. Never copy a private source into a public repository.
7. Deleting Actions runs, refs or repositories are separate destructive capabilities;
   do not request broader permissions merely to make a report look clean.
8. GitHub/provider behavior may change; use observed responses and current official
   docs rather than broadening access or switching identities to bypass policy.
