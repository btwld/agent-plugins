# Concepta Agent Plugins

Plugins for Codex and Claude Code. Maintain skills directly in this
repository; there is no upstream import, tracking, or merge workflow.

## Kits

| Plugin | Purpose | Skills | Version |
| --- | --- | --- | --- |
| [Product Kit](plugins/product-kit/README.md) | Research, requirements, PRDs, and delivery breakdowns | 6 | 0.3.2 |
| [Engineering Kit](plugins/engineering-kit/README.md) | Technical decisions, implementation, reviews, and verification | 11 | 0.1.1 |
| [Design Kit](plugins/design-kit/README.md) | Interface design, critique, accessibility, UX copy, and research planning | 10 | 0.1.0 |

Product Kit owns the shared requirements, questions, and decisions. Engineering
Kit turns settled scope into implementation work without creating a second
requirement baseline. Use the skill that matches the task; no automatic sequence
or handoff is required.

A [flattened source snapshot](agent-plugins.flattened.md) is available for review.
Binary assets are listed by hash; install plugins from their folders, not the snapshot.

## Install

Clone or register this repository. Install the kits in the client you use.

### Codex

```sh
codex plugin marketplace add https://github.com/conceptadev/agent-plugins.git
codex plugin add product-kit@conceptadev
codex plugin add engineering-kit@conceptadev
codex plugin add design-kit@conceptadev
```

### Claude Code

```sh
claude plugin marketplace add https://github.com/conceptadev/agent-plugins.git
claude plugin install product-kit@conceptadev
claude plugin install engineering-kit@conceptadev
claude plugin install design-kit@conceptadev
```

Start a new session afterward. In Codex, request the relevant skill. Claude
commands include `/product-kit:write-prd`, `/product-kit:write-wbs`, and
`/engineering-kit:writing-plans`. Use one active provider for each plugin namespace;
cloning or maintaining this repository does not replace installed plugins.

Dart/Flutter uses a separate official provider. See [Dart/Flutter setup](docs/external-plugins.md).
Neither kit duplicates its skills or MCP server.

## Maintain

Canonical content lives in `plugins/<kit>/skills/<skill>/`. Templates, scripts,
references, and fixtures stay inside their owning plugin so cached installations
remain portable. Codex and Claude share the same content:

- `.agents/plugins/marketplace.json`: Codex catalog.
- `.claude-plugin/marketplace.json`: Claude catalog.
- `plugins/<kit>/.codex-plugin/plugin.json`: Codex plugin metadata.
- `plugins/<kit>/.claude-plugin/plugin.json`: Claude plugin metadata.

Keep each kit's version identical in both manifests and use scoped release tags
such as `product-kit/v0.3.2`. Keep development cachebusters out of releases.
Source attribution and license notices are in each kit's `SOURCES.md`; they do
not define a maintenance workflow. Keep real project records and generated output
outside the plugins. Bundled examples are fictional.

## Validate

From the repository root:

```sh
uv run --with jsonschema==4.26.0 python -m unittest discover -s plugins/product-kit/scripts/tests
python3 -m unittest discover -s plugins/engineering-kit/tests
python3 -m unittest discover -s tests
claude plugin validate plugins/product-kit --strict
claude plugin validate plugins/engineering-kit --strict
claude plugin validate plugins/design-kit --strict
claude plugin validate . --strict
```

Use Skill Creator for skill edits and provider validators for packaging changes.
Test changed helpers and check that resources resolve from an isolated plugin copy.
Included behavioral fixtures are not executed by these commands; passing helper
and packaging tests does not prove automatic skill selection or model behavior.
See each kit's guide for runtime dependencies and generation commands.
