# Contributor instructions

Read applicable repository instructions and the relevant source before editing.
Keep changes scoped; preserve existing user work, public identifiers and security boundaries.
Start with aggregated read-only checks of Git status, recent history and relevant tests.
Use the native tooling already present; avoid dependencies or abstraction without a concrete need.
Use clear names, type hints, small testable functions and PEP 8 for Python tooling.

`plugins/cloudcodex-windows-bootstrap/` is the complete distributable package.
The bootstrap reference directory is canonical for shared contracts, and its
assets/ directory holds the canonical YAML workflow template;
use its existing sync tool to update strategy-local copies, then verify their equality.
Do not change runtime policy just to make a packaging test pass. Distinguish source revision,
synthetic CI revision and managed baseline; never weaken authorization or cleanup guards.
Treat remote write/approval outcomes as potentially asynchronous: before retrying or claiming
no side effects, reconcile exact provider refs, marker commits and workflow runs while preserving
the same run ID. Never duplicate CI resources from stale connector/task state. If delegated
context is incomplete, return the exact missing fields to the parent without writes.

Run `python -X utf8 tools/validate.py` before committing. It runs package regressions,
repository/distribution checks, resource synchronization and deterministic archive builds.
New checks must complement existing coverage, not silently replace it. Report tests that
were not executable and distinguish offline contract checks from real agent/Actions runs.

Keep GitHub CI/release configuration outside the plugin directory. Never put credentials,
private project reports, machine paths or account-specific plugin IDs into public source.
No automatic OpenAI submission or additional CI provider is part of this repository.
This repository is the implementation and release boundary for one plugin. The family marketplace lives in Tungsteno74/cloudcodex-helpers-marketplace; do not reintroduce a repository-local marketplace manifest unless explicitly requested.
