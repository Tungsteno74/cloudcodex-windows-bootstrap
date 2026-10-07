# Releasing

1. Update the package version, version assertions, and changelog.
2. Run `python -X utf8 tools/validate.py` and review the diff.
3. Merge the reviewed source to `main`.
4. Create and push an annotated tag matching the package version.

Example:

```sh
git tag -a v0.6.1 -m "Release 0.6.1"
git push origin v0.6.1
```

The release workflow validates the tagged revision, downloads the already verified
artifact, checks its checksum/version/source revision, and creates a GitHub prerelease.
It does not rebuild or overwrite the artifact.

Release assets:
- `cloudcodex-windows-bootstrap-<version>.zip`
- `SHA256SUMS`
- `release-manifest.json`

Validation jobs use read-only repository permissions. Only the isolated publish job
receives `contents: write`.

## Marketplace publication

The family catalog is maintained separately in
`Tungsteno74/cloudcodex-helpers-marketplace`. A plugin release and a marketplace
catalog update are separate operations; publishing a GitHub release does not
automatically change marketplace policy or perform an official OpenAI submission.

## Future publication

No automatic OpenAI submission is configured. Re-evaluate the official submission
process when public listing is planned. Add another CI provider only if GitHub Actions
cannot cover a concrete release requirement.

References:
- https://developers.openai.com/plugins/deploy/submission
- https://docs.github.com/en/actions/reference/security/secure-use
