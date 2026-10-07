# Installation

The distributable plugin lives at:

```text
./plugins/cloudcodex-windows-bootstrap
```

This repository is a plugin source, not a marketplace.

## CloudCodeX Helpers Marketplace

The recommended catalog source is the public family marketplace:

```sh
codex plugin marketplace add Tungsteno74/cloudcodex-helpers-marketplace
```

Browse that marketplace, install **CloudCodeX Windows Bootstrap**, and connect the
required GitHub app.

Workspace administrators can import:

```text
https://github.com/Tungsteno74/cloudcodex-helpers-marketplace
```

Leave **Path** empty and select a branch, tag, or commit as needed. Marketplace
import does not grant GitHub access; normal workspace and app permissions still apply.

## Local source development

Clone this repository when working on the plugin implementation directly. A local
marketplace can point at `./plugins/cloudcodex-windows-bootstrap`; the implementation
repository intentionally does not embed a family marketplace.

## Standalone package

Tagged GitHub releases contain a ZIP with the plugin at archive root. The package
includes the portable and Codex manifests plus the GitHub app binding; it does not
ship credentials or a custom MCP server.

GitHub distribution and official OpenAI publication are separate channels.

References:
- https://developers.openai.com/plugins/build/plugins
- https://help.openai.com/en/articles/20001504-importing-and-syncing-plugin-marketplaces-from-github
