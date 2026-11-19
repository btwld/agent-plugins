# Dart Package Kit

Four skills for projects that use ACK, Noir, Mix, or Remix. Each starts with the version resolved by the consuming project. You can use this kit alongside the official Dart and Flutter plugin.

| Skill | When to use it | Example request |
| --- | --- | --- |
| [ack](skills/ack/SKILL.md) | Validate structured input with the Dart ACK schema library. | “Validate this API response with ACK and show how to report a missing field.” |
| [noir](skills/noir/SKILL.md) | Build or debug an interactive terminal UI using Dart Noir. | “Show the selected row in my Noir terminal list and handle keyboard navigation.” |
| [mix](skills/mix/SKILL.md) | Style Flutter widgets using Mix tokens, modifiers, and variants. | “Give this Mix-styled panel different padding at the compact breakpoint.” |
| [remix-flutter](skills/remix-flutter/SKILL.md) | Build a Flutter interface with Remix components and the project's theme or presets. | “Use our Remix buttons for this form and preserve the loading state.” |

## Install

After registering the marketplace, run `codex plugin add dart-package-kit@conceptadev` or `claude plugin install dart-package-kit@conceptadev`. Start a fresh session. In Codex, try `$ack`. In Claude Code, try `/dart-package-kit:remix-flutter`.

If you already load a package's own skill, choose one entry for that task to avoid competing instructions. For a general SDK or framework task, use the official Dart and Flutter plugin. Package references and credits are in [SOURCES.md](SOURCES.md).
