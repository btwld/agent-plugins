---
name: flutter-setup
description: Check or configure Flutter’s official skills and Dart MCP in the environment where the agent runs. Invoke explicitly for setup, troubleshooting, or a readiness check.
disable-model-invocation: true
---

# Flutter setup

Identify the client and the machine that owns the project checkout. A terminal inside a chat sandbox may belong to a different environment from the account the user wants to configure. Apply changes only to the requested target. For a readiness check, inspect the environment without changing its configuration.

1. In a coding environment, run `dart --version` and `flutter --version` on the agent’s PATH. Honor the project’s pinned SDK. Inspect the client’s enabled plugins, available skills, and MCP servers. Record any existing Dart server or overlapping skill provider before proposing changes.
2. For a requested install in Codex CLI, register `https://github.com/flutter/agent-plugins.git` with `codex plugin marketplace add`, then run `codex plugin add dart-flutter@dart-flutter`. In Claude Code CLI, run `claude plugin install dart-flutter --marketplace flutter/agent-plugins`. Skip an already enabled installation. The official plugin configures `dart mcp-server`; adding another server entry would start a second copy.
3. For a hosted coding environment, verify SDK availability and plugin loading inside the actual runner. For a replacement or ephemeral runner, use its supported image, environment setup, or project configuration. For a hosted chat account, use that product’s plugin or connector settings. Check which components it loads and whether it accepts a command or requires a hosted MCP URL. A shell install affects the shell’s client profile.
4. After installation, reload the client if needed. During a check-only request, report a pending reload and preserve the running session. Check for an official skill such as `flutter-add-widget-test` and ask the Dart MCP server for its tools. Record the response. If only a separate process probe was possible, distinguish it from an in-session connection. Report the target, SDK versions, plugin, skill discovery, and MCP status. Name any remaining step, such as opening a fresh session or connecting a remote endpoint.

[Official Flutter setup](https://docs.flutter.dev/ai/get-started)
