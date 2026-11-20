---
name: noir
description: Build, debug, or test Dart terminal user interfaces that use package:noir. Use for Noir widgets, terminal layout, focus and keyboard input, reactive state, and drive-mode inspection. Use the framework contributor guide for renderer internals. Ordinary Dart command-line tools, Flutter screens, and Noir zero-knowledge circuits have separate tooling.
---

# Noir terminal applications

Start from the application entry point and its resolved dependency. Check `pubspec.lock` for the Noir version and `.dart_tool/package_config.json` for the package source. A path or workspace dependency may contain newer APIs than the published release. Match constructors and tooling to the resolved library, especially for `noir_signals` and `noir_driver`.

Use `package:noir/noir.dart` and `runTuiApp` for application UI. For a first screen, start with a single text widget.

```dart
import 'package:noir/noir.dart';

void main() => runTuiApp(const Text('Ready'));
```

For an existing app, build on the closest widget and follow its state ownership. Size layouts in character cells. For a keyboard interaction, trace the event from the app handler to the focused widget. Give driven controls stable `ValueKey<String>` identifiers so the driver can target them. Dispose caller-owned controllers and focus nodes with their owner.

The following upstream guidance was checked against Noir 0.0.7. Read the relevant section of [Noir’s application skill](https://github.com/btwld/noir/blob/noir-v0.0.7/skills/noir/SKILL.md). Its adjacent references cover [widgets and layout](https://github.com/btwld/noir/blob/noir-v0.0.7/skills/noir/references/widgets.md), [input and focus](https://github.com/btwld/noir/blob/noir-v0.0.7/skills/noir/references/inputs-and-focus.md), and [Signals and hooks](https://github.com/btwld/noir/blob/noir-v0.0.7/packages/noir_signals/doc/hooks.md). When working offline, use the resolved package's public exports and examples.

Check the result at the layer the user cares about. Run `dart analyze` and focused application tests. A headless mount checks lifecycle; for a layout or input change, exercise the interaction in a terminal or with a compatible `noir_driver`, and inspect the rendered frame at the relevant terminal size. Report the behavior observed and any terminal-dependent checks still open. [Noir testing guide](https://btwld.github.io/noir/docs/testing/)

When the deliverable is a recorded demo, use the recorder from the matching Noir repository checkout. Under `packages/noir/`, run `dart run tool/record_noir_demo.dart --recipe <recipe.json>` with the example and terminal size you want to show. Replay the cast and check that it shows the requested interaction. [Noir 0.0.7 recording workflow and recipe schema](https://github.com/btwld/noir/tree/noir-v0.0.7/skills/record-noir-demo)
