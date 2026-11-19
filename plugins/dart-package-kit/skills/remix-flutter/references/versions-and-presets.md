# Remix versions and presets

The Dart package is `remix`, published from `btwld/remix`. Both API lines below
use `package:remix/remix.dart` and re-export Mix. The resolved source remains
authoritative for later releases.

| Published API | Button styler | Theme and installation |
| --- | --- | --- |
| Stable `0.2.0` | `RemixButtonStyle` | The package exports `FortalScope` and `FortalButtonStyle` as well as its base widgets. [Released source](https://pub.dev/api/archives/remix-0.2.0.tar.gz) |
| Prerelease `1.0.0-rc.4` | `ButtonStyler` | Base widgets ship without a theme. The CLI installs editable preset recipes and theme files when wanted. This release requires Flutter 3.44 and Dart 3.12 or newer within its SDK constraints. [Released source](https://github.com/btwld/remix/tree/remix-v1.0.0-rc.4/packages/remix) |

Use the [pub.dev versions page](https://pub.dev/packages/remix/versions) to
check published candidates before adding dependencies. In an existing app,
keep the resolved release line unless the task calls for an upgrade. For a Git
or path dependency, use its source even when the manifest version matches a Pub
release. When docs and source differ, check the public export barrel, component
constructor, and generated styler of the resolved source.

## Direct widget examples

Use one of these button implementations inside the existing Flutter host. The
0.2.0 package uses the earlier convenience methods.

```dart
import 'package:flutter/widgets.dart';
import 'package:remix/remix.dart';

Widget saveButton(VoidCallback save) => RemixButton(
  label: 'Save',
  onPressed: save,
  style: RemixButtonStyle()
      .paddingX(16)
      .paddingY(10)
      .color(const Color(0xFF244B8F))
      .borderRadiusAll(const Radius.circular(8))
      .label(TextStyler().color(const Color(0xFFFFFFFF))),
);
```

The 1.0.0-rc.4 implementation uses the component's `ButtonStyler` with Mix
shorthand supported by the resolved version.

```dart
import 'package:flutter/widgets.dart';
import 'package:remix/remix.dart';

Widget saveButton(VoidCallback save) => RemixButton(
  label: 'Save',
  onPressed: save,
  style: ButtonStyler()
      .padding(.horizontal(16))
      .padding(.vertical(10))
      .color(const Color(0xFF244B8F))
      .borderRadius(.circular(8))
      .label(TextStyler().color(const Color(0xFFFFFFFF))),
);
```

For other components, consult the exact [stable API](https://pub.dev/documentation/remix/0.2.0/)
or [release candidate component docs](https://github.com/btwld/remix/tree/remix-v1.0.0-rc.4/docs/components).

## Preset workflows on the 1.0 release candidate line

Direct widget use requires only the `remix` dependency. For a fresh app opting
into the release candidate registry workflow, verify the CLI and package
constraints and check that the official `registry-stable` ref exists. The CLI's
`init` command needs that ref to create a new `remix.yaml`. If it is unavailable,
report the registry blocker. Direct widgets can still be used when they satisfy
the task. [CLI release source](https://github.com/btwld/remix/tree/remix_cli-v1.0.0-rc.1/packages/remix_cli)

```sh
flutter pub add 'remix:^1.0.0-rc.4'
dart pub global activate remix_cli '^1.0.0-rc.1'
remix init --preset vanilla
remix add button
```

An unversioned Pub install selects the stable line, including the earlier
CLI `0.1.0`. Where the app already pins the CLI as a dev dependency, use its
project-local invocation such as `dart run remix_cli:remix list`.

- **Add items.** `remix list` reads the pinned catalogs. The CLI installs an
  item's dependency closure, which can include theme files. Use the current
  `remix.yaml` prefix and UI path to locate and import the owned barrel and
  theme. Preset and prefix are independent. [Registry installation](https://fluttermix.com/remix/docs/open-code/install/)
- **Refresh owned source.** `remix registry update @remix` resolves the
  configured ref and moves its pin. Supply `--ref <newer-ref>` to move off a
  SHA or tag or to select a different release ref.
  `remix add <items> --diff` previews template differences, including local
  edits. `--overwrite` replaces named items and does not merge. Keep authored
  changes and review which items need refreshing, including `theme` where
  applicable. [Registry updates](https://fluttermix.com/remix/docs/open-code/updating/)
- **Read pin-specific guidance.** Prefer the app's installed `using-remix`
  skill or read it at the registry SHA. If the project uses `remix skills
  install`, compare `remix.skills.json` with the `@remix` revision before
  using those instructions. The installation command writes project skill
  files and an `AGENTS.md` block. [CLI skill setup](https://fluttermix.com/remix/docs/open-code/install/#agent-skills)

For current docs and deeper upstream guidance, consult the [Remix docs](https://fluttermix.com/remix/docs/), [package changelog](https://pub.dev/packages/remix/changelog), and [upstream skills](https://github.com/btwld/remix/tree/main/skills).
