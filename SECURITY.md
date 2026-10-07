# Security

The plugin uses the user's authorized GitHub app and ships no credentials or server.
AUTO never overrides repository policy, provider approvals, or permission scope.

A validation run may create a disclosed branch and consume GitHub Actions quota.
Interrupted runs can leave a branch that requires manual cleanup.

Do not post tokens, private source, or sensitive logs in public issues. Use GitHub
private vulnerability reporting when available, or request a private contact channel.

Repository validation is read-only. Only the isolated release publishing job receives
write permission for release assets.
