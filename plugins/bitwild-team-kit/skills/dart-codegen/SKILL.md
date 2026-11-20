---
name: dart-codegen
description: "Use when authoring, modifying, or debugging Dart code generators with build_runner, source_gen, code_builder, build, build_test, or analyzer APIs. Covers generator internals, build.yaml builder definitions, phase ordering, generated annotation APIs, analyzer or type inspection inside generators, and generator test failures. Do not use for ordinary Dart or Flutter app code, or when only consuming an existing generator unless the task is to debug the generator itself."
---

# Dart Code Generation

Implement and debug Dart generators using the builder and package versions in the target repository. Generator APIs change frequently, so inspect the installed `build`, `source_gen`, `analyzer`, `code_builder`, and `dart_style` versions before choosing exact APIs.

Dart's macros experiment was discontinued. For package-integrated source generation, use the current `build_runner`/`build` ecosystem unless the user has chosen a different generation mechanism.

## Establish the generator contract

Before implementing, determine:

- the input asset and generated output;
- whether output is a part of the input library or a standalone importable library;
- whether generation is per-input or aggregates multiple assets;
- whether generated code must access private declarations;
- who consumes the annotations and whether annotation and implementation packages need separate release lifecycles;
- the target package's SDK and dependency constraints.

Do not choose a two-package layout, `SharedPartBuilder`, or `code_builder` merely as a default. Select them when the output contract or package distribution requires them.

## Builder selection

| Required output | Typical choice |
|---|---|
| Contributions combined into `.g.dart` | `SharedPartBuilder` with one or more `Generator`s |
| Dedicated part file | `PartBuilder` |
| Standalone Dart library with its own imports | `LibraryBuilder` |
| Aggregated or non-Dart output | A raw `Builder`, often with a synthetic input |
| Post-build transformation | `PostProcessBuilder` |

Part output shares the source library's imports and can access private declarations. A standalone library owns its imports but cannot access private declarations from another library.

## Implementation rules

- Declare every output written by a raw builder in `buildExtensions`.
- Avoid reading a builder's own output. Model multi-stage work as separate builders with declared inputs and ordering.
- Use `InvalidGenerationSource` with an `element` or node when invalid annotated source should produce a source-located diagnostic. Returning no output can be correct when the element simply does not apply.
- Use current `TypeChecker.typeNamed` or `typeNamedLiterally` for normal type matching. `TypeChecker.fromRuntime` was removed, and `fromUrl` is a brittle fallback for cases that intentionally depend on a specific library URI.
- For `SharedPartBuilder`, `PartBuilder`, and `LibraryBuilder`, account for the version's built-in output formatting before adding another formatting pass. Current `source_gen` builders format with the input library's effective language version by default.
- Use `DartEmitter.scoped()` for a standalone `Library` when automatic imports are required. For part output, do not emit import directives; the owning library must make referenced types available.
- Prefer readable templates for simple fixed output. Use `code_builder` when the generated structure or import allocation is sufficiently dynamic to justify its fluent model.
- Keep annotation packages free of generator-only dependencies when they are runtime dependencies of consumers. A single package is acceptable when annotations are not separately consumed or the repository intentionally keeps the implementation together.

## Workflow

1. Inspect `pubspec.yaml`, `build.yaml`, the builder factory, existing generated files, and generator tests.
2. Choose the builder from the required output shape.
3. Define or correct `buildExtensions` and relevant `build.yaml` configuration.
4. Implement the smallest generator behavior that satisfies the contract.
5. Add tests for the changed behavior and important diagnostics. Do not manufacture interfaces, builders, or package splits solely to satisfy a template.
6. Run the focused generator tests and an end-to-end build in a fixture or example package when available.

Use the repository's build command. A common smoke test is:

```bash
dart run build_runner build --delete-conflicting-outputs
```

Use `--delete-conflicting-outputs` only when generated outputs are expected to be replaced; report conflicts rather than deleting user-authored files of uncertain ownership.

## Task references

Read only what the task needs:

- [architecture.md](references/architecture.md) — builder and package-layout decisions
- [build_yaml.md](references/build_yaml.md) — builder registration and target configuration
- [dependencies.md](references/dependencies.md) — multi-phase and aggregate generation
- [analyzer_api.md](references/analyzer_api.md) — elements, types, annotations, and `TypeChecker`
- [code_builder.md](references/code_builder.md) — import-aware standalone output and part-output constraints
- [testing.md](references/testing.md) — `build_test` and resolver-based tests
- [troubleshooting.md](references/troubleshooting.md) — cycles, caches, missing parts, and rebuild storms
- [worked_example.md](references/worked_example.md) — a complete example to adapt after choosing the same output shape
- [practical_patterns.md](references/practical_patterns.md) — options, assets, logging, and migration cautions
- [real_world.md](references/real_world.md) — examples from established generator packages

## Completion evidence

- The builder type matches the actual output and privacy requirements.
- `buildExtensions` and `build.yaml` agree with every written asset.
- Part output does not attempt to own imports; standalone output handles imports safely.
- Type and analyzer APIs match the installed dependency versions.
- Focused tests and an appropriate smoke build pass, or the unverified gap is explicit.
