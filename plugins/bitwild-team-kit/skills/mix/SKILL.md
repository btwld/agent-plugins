---
name: mix
description: Use when a Flutter task asks to change package:mix styles, layout primitives, tokens, or variants, or diagnose how a Mix styler resolves on a widget. Remix component behavior and generic Flutter layout have separate workflows.
---

# Style Flutter widgets with Mix

Find the widget that renders the affected surface and the style it receives. Check the resolved `mix` version in `pubspec.lock`. For path or Git dependencies, follow the package location in `.dart_tool/package_config.json`. Use that source to check the actual constructor, styler methods and token types before editing.

Work at the point that owns the appearance. To change a single widget, compose the appropriate concrete styler and pass it to that widget. Return or assign the new style from each fluent call. To change a shared design value, trace the token to its enclosing `MixScope` and identify which other widgets inherit it. For a state-specific change, inspect which widget supplies the hover, focus or press state. Keep changes to Remix component behavior, selection or semantics in the component that owns them.

For example, this Mix 2.4 widget adds a uniform inset to its child. Reuse the application's spacing token when one exists.

```dart
import 'package:flutter/widgets.dart';
import 'package:mix/mix.dart';

Widget insetPanel(Widget child) =>
    Box(style: BoxStyler().padding(.all(12)), child: child);
```

Exercise the changed property in the consuming app. A spacing test can measure the distance between a keyed child and its parent. For a hover or theme change, exercise both states and inspect the visible result. Run the targeted widget test and Flutter analyzer using the project's SDK.

For version-specific examples, start from the installed package and the upstream guide for the relevant API. The Mix repository publishes its own full skill, with focused guides to layouts, variants, tokens, generators and testing. [Mix 2.4.0 skill](https://github.com/btwld/mix/tree/mix-v2.4.0/skills/mix) · [Documentation index for agents](https://raw.githubusercontent.com/btwld/mix/mix-v2.4.0/llms.txt) · [Published versions](https://pub.dev/packages/mix/versions)
