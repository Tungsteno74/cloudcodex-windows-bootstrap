# CloudCodeX Windows Bootstrap

**Windows validation for Codex Cloud with safe fallbacks and no default-branch writes.**

[![Validate](https://github.com/Tungsteno74/cloudcodex-windows-bootstrap/actions/workflows/validate.yml/badge.svg)](https://github.com/Tungsteno74/cloudcodex-windows-bootstrap/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

CloudCodeX Windows Bootstrap is a multi-skill plugin that lets a Linux Codex Cloud
environment validate Windows-only checks through GitHub Actions. It does not provide
an interactive Windows desktop.

This repository is the independent source and release boundary for the plugin.
Discovery is handled separately by the
[CloudCodeX Helpers Marketplace](https://github.com/Tungsteno74/cloudcodex-helpers-marketplace)
under the **GSM (GPT Structured Marketplace)** architecture.

## How it works

```text
matching existing CI
  -> strict ephemeral branch
  -> managed branch
  -> eligible fork
  -> retained ephemeral branch
```

Interactive and unknown contexts default to **CONFIRM**. Positively identified
delegated or unattended runs default to **AUTO**. Explicit user choices always win,
and AUTO never expands permissions, credentials, or policy scope.

If GitHub tools are unavailable during onboarding, the plugin can return
`DEFERRED_TO_TASK` so a later Cloud task can resume the pending Windows validation.

## Install

The recommended catalog source is the family marketplace:

```sh
codex plugin marketplace add Tungsteno74/cloudcodex-helpers-marketplace
```

Then install **CloudCodeX Windows Bootstrap** and connect the required GitHub app.

For source-level development, clone this repository directly. The distributable plugin
lives at `./plugins/cloudcodex-windows-bootstrap`; this repository intentionally does
not contain its own marketplace manifest.

Tagged [GitHub Releases](https://github.com/Tungsteno74/cloudcodex-windows-bootstrap/releases)
contain the standalone plugin ZIP, checksum file, and source revision manifest.
GitHub distribution is separate from any official OpenAI directory publication.

## Repository layout

```text
.github/workflows/                    # Validation and release pipelines
plugins/cloudcodex-windows-bootstrap/ # Complete distributable plugin
tests/                                # Distribution tests
tools/                                # Validation and deterministic packaging
docs/                                 # Installation, release and project status
```

## Develop

Use Python 3.9+ in an isolated environment:

```sh
python -m venv .venv
python -m pip install -r requirements-dev.txt
python -X utf8 tools/validate.py
python -X utf8 tools/build_release.py
```

Validation runs package and distribution tests, checks duplicated strategy resources,
and verifies reproducible ZIP output on Linux and Windows CI.

## Status

**0.6.2 is pre-1.0.** Delegated AUTO, authorization escalation, managed cleanup,
and Local/Cloud Windows execution are validated. Remaining coverage focuses on
strict deletion, fork, concurrency, interrupted execution, and lease conflicts.

See [project status](docs/PROJECT_STATUS.md), [validation status](docs/test-status.md),
[runtime resilience guidance](docs/runtime-resilience.md), and
[release process](docs/releasing.md). Licensed under [MIT](LICENSE).
