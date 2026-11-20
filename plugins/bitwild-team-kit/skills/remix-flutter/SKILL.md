---
name: remix-flutter
description: >-
  Use when adding, styling, debugging, or upgrading Remix widgets in a Flutter
  app that uses btwld/remix, package:remix/remix.dart, or a remix.yaml registry.
  Covers version-specific component stylers, app-owned Vanilla, Fortal, and
  HeroUI presets, theme and overlay setup, and remix_cli registry changes.
  The Flutter package is distinct from React Remix, standalone Mix styling, and
  standalone naked_ui primitives.
---

# Remix for Flutter

## Identify the API the app uses

1. Read the owning Flutter app's `pubspec.yaml`, `pubspec.lock`, and
   `remix.yaml` if present. Check the resolved `remix`, `mix`, `naked_ui`, and
   any `remix_cli` versions, the Flutter SDK, and dependency overrides. Use
   `.dart_tool/package_config.json` to locate the resolved package source. For
   a Git or path dependency, inspect the actual revision or checkout.
2. Inspect nearby components and local theme setup. In a registry project,
   find the configured preset, prefix, UI path, and registry revision. Read the
   app-owned recipes, barrels, generated wrappers, and any installed upstream
   Remix skill for that revision. The package version and registry revision are
   independent.
3. Confirm each unfamiliar constructor, style method, behavior root, or CLI
   option against the resolved package and matching upstream material. Use the
   [version and preset reference](references/versions-and-presets.md) to locate
   the right source before applying examples from the website.

## Work in the app's existing layer

- **Direct widgets.** Use the exported `Remix*` widget, its matching styler, and
  existing app tokens. Keep behavior in the public component and its group or
  controller. Check the component's reported states before styling selected,
  disabled, or focus variants.
- **App-owned presets.** Use the configured prefix and local `ui.dart` barrel.
  Choose the installed constructor or runtime variant for the requested visual
  intent. When the local wrapper supports `style:`, use it for a single-instance
  override. Edit the app's recipe or theme for changes that should apply across
  the app. Regenerate adapters with the app's code-generation command after
  changing annotated inputs.
- **Registry changes.** Check the pinned catalog and installed ownership records
  before adding or refreshing items. Review a diff before replacing existing
  owned code and retain intentional local changes. For reusable presets or
  published registries, locate the authoring guide at the registry revision. Validate the catalog, install the theme and one component into a fresh consumer using its chosen prefix, and run that consumer’s analyzer and widget test. [Registry authoring at RC.5](https://github.com/btwld/remix/tree/remix-v1.0.0-rc.5/skills/building-remix-design-system)
- **Host and interaction.** Place the installed theme above the Navigator when
  routes and overlays consume its tokens. Verify the resolved component's host
  requirements. Check overlays for menus and text selection, a Navigator for
  dialogs, and the toast scope where the resolved API provides it. For preset
  details, read the installed `using-remix` skill or find its source by
  replacing `main` in the upstream link with the `@remix` revision.
  [Using Remix](https://github.com/btwld/remix/tree/main/skills/using-remix)

Remix owns component composition. Mix provides stylers, variants, and tokens.
Naked UI supplies interaction behavior. For a standalone Mix or Naked UI task,
use that package's public API and documentation.

## Verify

Run the project's formatter, `flutter analyze`, and relevant Flutter widget
tests. Exercise the behavior that changed, including applicable keyboard focus,
activation, selected or disabled states, and overlay opening and dismissal.
For generated wrappers, confirm the build output and final imports agree with
the installed prefix. Report the resolved version or revision and the checks
that ran. When execution is unavailable, report source verification separately.
