# Generator Architecture

Choose architecture from the generated asset contract. Examples from popular packages are useful evidence, not mandatory templates.

## Builder decision

| Need | Builder |
|---|---|
| Contributions combined into one `.g.dart` part | `SharedPartBuilder` |
| A dedicated part extension such as `.freezed.dart` | `PartBuilder` |
| A standalone importable Dart file | `LibraryBuilder` |
| Many inputs aggregated into one output | Raw `Builder` with a synthetic input and `findAssets` |
| JSON, SQL, or another non-Dart output | Raw `Builder` |
| Cleanup or compression after ordinary builders | `PostProcessBuilder` |

`SharedPartBuilder` writes intermediate part fragments that `source_gen|combining_builder` combines. Its builder configuration normally uses cache output and applies the combining builder. Give each shared-part builder a distinct `partId` to avoid fragment collisions.

`PartBuilder` owns a dedicated part extension. Do not use `.g.dart`, which is reserved for combined shared-part output.

`LibraryBuilder` emits a separate library that can own imports. It cannot access private declarations from the input library. Choose a part-based builder when private access is required.

## Package layout

Split annotations and generator implementation when:

- application code imports annotations at runtime;
- consumers should not receive `analyzer`, `build`, or `source_gen` as runtime dependencies;
- the annotations and generator have distinct public APIs or release responsibilities.

A common distribution is:

```text
foo_annotation/   # annotation API used by source packages
foo_generator/    # builder and generator implementation, used as a dev dependency
```

Keep one package when annotations are internal to the generator package, the tool is repository-local, or a split would add release overhead without protecting consumers. Check the actual dependency graph rather than describing every collapsed package as non-production.

## Output location

- `build_to: cache` keeps intermediates under build cache and is appropriate for shared-part fragments.
- `build_to: source` writes visible source files and is restricted by the build system to appropriate targets, commonly the root package.

Generated source checked into version control is a repository policy choice. Preserve the existing policy unless the user asks to change it.

## Application scope

- `none` requires explicit target configuration.
- `dependents` applies to packages depending on the builder package.
- `all_packages` applies across the dependency graph and should be used only when that broad scope is intentional.
- `root_package` applies to the top-level package and is common for application-wide aggregators.

Verify exact `build.yaml` keys against the installed `build_config`/`source_gen` versions before migrating old configuration.
