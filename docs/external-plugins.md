# Official Dart and Flutter

Use `dart-flutter@dart-flutter` from the official
[Flutter plugin repository](https://github.com/flutter/agent-plugins).
Follow its [setup guide](https://docs.flutter.dev/ai/get-started) for SDK and client
requirements. This provider is separate from the company-owned Product and
Engineering kits; its skills and Dart MCP server are not copied into this repo.

## Install

With the Dart SDK on your client's PATH, use the desired client:

```sh
# Codex
codex plugin marketplace add https://github.com/flutter/agent-plugins.git
codex plugin add dart-flutter@dart-flutter

# Claude Code
claude plugin marketplace add https://github.com/flutter/agent-plugins.git
claude plugin install dart-flutter@dart-flutter
```

The plugin configures `dart mcp-server`. Avoid duplicate Dart skill providers or
MCP configurations. A new session should expose the selected skills and server;
installation alone does not establish successful application testing.

## Update the external provider

Use the client's native plugin manager when an update is wanted:

```sh
# Codex
codex plugin marketplace upgrade dart-flutter
codex plugin add dart-flutter@dart-flutter

# Claude Code
claude plugin marketplace update dart-flutter
claude plugin update dart-flutter@dart-flutter
```

A catalog refresh is not itself a plugin reinstallation. Inspect the selected
version, apply the update, and verify the relevant workflow in a new session.
These commands update an external installation; they do not merge source into
this repository or schedule background synchronization.

If Codex does not fetch updates, inspect `codex plugin marketplace list --json`.
The marketplace source should be `git` with the official repository URL, not a
local cache directory. Re-register the URL above when that is the intended source.
