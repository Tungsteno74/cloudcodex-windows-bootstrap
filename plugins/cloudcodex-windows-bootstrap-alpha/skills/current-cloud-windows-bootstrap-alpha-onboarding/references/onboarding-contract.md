# Alpha onboarding contract

This contract is valid only during actual Cloud Current environment onboarding and
only after an explicit Alpha request. It is not an authorization to create,
publish, approve, or modify a Cloud environment outside the host's exposed draft
API.

Read the current draft first. Preserve `startup` and `start_skill` byte-for-byte.
If `install_script` is nonempty, preserve it; an exact match is already present and
a different value requires `ALPHA_INSTALL_DRAFT_MERGE_NEEDED`. Never concatenate,
replace, or infer a merge.

When the supported draft API is present and `install_script` is empty, submit only
the runtime schema's `install_script` field containing the bundled asset bytes.
Read back when the API permits it. A timeout, approval transition, or ambiguous
response is not success: return an uncertain/blocked result with the asset.

If native skill-resource reading is unavailable, use a filesystem fallback only to
obtain this package's local asset; it says nothing about normal-task availability.
If no host draft API exists, return `ALPHA_INSTALL_DRAFT_BLOCKED` with the exact
asset. Do not assert client-side native injection or that Root follow-ups can solve
the missing capability. No credentials, authentication bypass, CI, publication,
approval, startup, or start_skill changes are allowed.
