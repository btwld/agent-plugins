# Official Dart and Flutter

Use `dart-flutter@dart-flutter` from the official
[Flutter plugin repository](https://github.com/flutter/agent-plugins).
Follow its [setup guide](https://docs.flutter.dev/ai/get-started) for SDK and client
requirements. The official provider supplies the general skills and the Dart MCP
server. Bitwild Team Kit supplies the specialist Dart, Flutter, and package workflows.
[Team skill catalog](../plugins/bitwild-team-kit/README.md)

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

## Hosted environments

Install for the client that owns the project checkout. Each machine or cloud runner needs access to the SDK. In an ephemeral environment, put SDK provisioning in its image or setup script and verify discovery in a fresh session.

| Target | How to configure it |
| --- | --- |
| Codex CLI on a remote machine | Use the Codex commands above in the runner’s active profile. Check that an official skill is visible and that Dart MCP returns tools there. [Codex cloud environments](https://developers.openai.com/codex/cloud/environments/) |
| Claude.ai chat | In **Customize → Plugins → Add marketplace**, add `flutter/agent-plugins` and select Dart and Flutter. Chat loads skills. Its MCP connectors require a remote URL, while Flutter ships a local command. [Claude platform support](https://claude.com/docs/plugins/platform-support) |
| Claude Code on the web | Provision the SDK in the cloud environment. For a single-repository session, a project `.mcp.json` can register `dart mcp-server` when no plugin provides it. Check the account’s enabled skills in the cloud session. [What carries over](https://code.claude.com/docs/en/cloud-environments#what-carries-over-from-your-setup) |
| Grok Bot | Search **Connect apps** for Dart and Flutter. If unavailable, provision Dart on the Bot’s computer and add a **Command** connector with command `dart` and argument `mcp-server`. This configures MCP only. [Bot connectors](https://docs.x.ai/grok-bot/computer-and-apps#connect-an-app) |
| ChatGPT chat | On a workspace with custom apps enabled, connect a hosted HTTPS MCP endpoint through the app settings. Flutter supplies a command to run beside the checkout. A hosted connector needs its own runtime and access to the intended project. [Connect a custom MCP app](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt/) |

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
