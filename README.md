# Bitwild Team Kit

One plugin for Bitwild's product, design, engineering, and specialist Dart and Flutter workflows. Pick the task you need: define a requirement, break work into delivery packages, design an interface, write for people or agents, or give a change its final code review. [Browse the team workflows](plugins/bitwild-team-kit/README.md)

## Install

The GitHub repository is `btwld/agent-plugins`. Its marketplace ID is `conceptadev`; the installable plugin is `bitwild-team-kit`.

**Codex**

```sh
codex plugin marketplace add https://github.com/btwld/agent-plugins.git
codex plugin add bitwild-team-kit@conceptadev
```

**Claude Code**

```sh
claude plugin marketplace add https://github.com/btwld/agent-plugins.git
claude plugin install bitwild-team-kit@conceptadev
```

Open a fresh session. Try `$deep-code-review` in Codex or `/bitwild-team-kit:deep-code-review` in Claude Code. For ACK schemas, Noir terminal apps, Mix styling, or Remix components, invoke `ack`, `noir`, `mix`, or `remix-flutter` under the same plugin.

The official Flutter plugin supplies general SDK skills and Dart MCP. Install it alongside the team kit when you need those tools. [Official Dart and Flutter setup](docs/external-plugins.md)

## Switch from the previous kits

1. If `conceptadev` is already registered, refresh it with `codex plugin marketplace upgrade conceptadev` or `claude plugin marketplace update conceptadev`.
2. Install `bitwild-team-kit@conceptadev`. Check that the new plugin lists the skills you use.
3. Remove the former company kits you installed: `engineering-kit`, `product-kit`, `design-kit`, and `dart-package-kit`. For example, run `codex plugin remove engineering-kit@conceptadev` or `claude plugin uninstall engineering-kit@conceptadev` in its original scope. Open a fresh session.
4. Update saved Claude commands to the new prefix. For example, `/product-kit:write-wbs` becomes `/bitwild-team-kit:write-wbs`. The skill names stay the same. Scripts that used a checkout path should now resolve resources under `plugins/bitwild-team-kit/`.

## Validate

```sh
python3 -m unittest discover -s tests
python3 -m unittest discover -s plugins/bitwild-team-kit/tests
uv run --with jsonschema==4.26.0 python -m unittest discover -s plugins/bitwild-team-kit/scripts/tests
claude plugin validate plugins/bitwild-team-kit --strict
claude plugin validate . --strict
```

Maintain runtime files in the plugin directory. Match versions across provider manifests and use plugin-scoped release tags such as `bitwild-team-kit/v1.0.0`. The [older flattened snapshot](agent-plugins.flattened.md) records an earlier layout. [Source credits and licensing](plugins/bitwild-team-kit/SOURCES.md)
