# Practical Generator Patterns

Use these patterns for generator implementation details that do not belong in the main workflow.

## Builder options

`BuilderOptions.config` is a `Map<String, dynamic>`. Read only supported keys, validate useful error cases, and provide defaults where the option is optional:

```dart
Builder autoLabelBuilder(BuilderOptions options) {
  final strict = switch (options.config['strict']) {
    null => false,
    final bool value => value,
    _ => throw ArgumentError.value(
        options.config['strict'],
        'strict',
        'must be a boolean',
      ),
  };

  return SharedPartBuilder(
    [AutoLabelGenerator(strict: strict)],
    'auto_label',
  );
}
```

Keep the top-level factory synchronous and deterministic. Do file and resolver work inside the builder or generator, where a `BuildStep` is available.

## LibraryReader

`LibraryReader` provides generator-focused access to a resolved library:

```dart
class AutoLabelLibraryGenerator extends Generator {
  @override
  String generate(LibraryReader library, BuildStep buildStep) {
    const checker = TypeChecker.typeNamed(
      AutoLabel,
      inPackage: 'auto_label_annotation',
    );

    for (final annotated in library.annotatedWith(checker)) {
      final element = annotated.element;
      final annotation = annotated.annotation;
      // Generate from the related declarations.
    }

    return output;
  }
}
```

Use it when generation needs relationships among several declarations in one library. `GeneratorForAnnotation` is simpler for independent annotated elements.

## AssetId rules

- Every asset written by a raw builder must match an output declared in `buildExtensions`.
- Paths are package-relative, such as `lib/src/model.dart`, not absolute paths.
- `changeExtension` replaces the final extension; `addExtension` appends one.
- Aggregators using a synthetic input usually construct their final `AssetId` explicitly.

Do not infer that an asset can be written merely because the path is under the package root.

## Shared-part generators

Several `Generator`s can contribute through one `SharedPartBuilder`:

```dart
Builder packageBuilder(BuilderOptions options) => SharedPartBuilder(
  [ModelGenerator(), EnumGenerator()],
  'package_name',
);
```

Use one shared builder when the generators intentionally contribute to the same combined part. Separate them when options, activation, ordering, or ownership differ.

## Unresolved annotations

`GeneratorForAnnotation` normally reports unresolved annotations. Override `throwOnUnresolved` only when unresolved states are expected during a deliberate multi-phase build; silently skipping a genuinely missing type can hide a user error.

## Logging and diagnostics

Use the build system's logger for build progress and warnings. Use `InvalidGenerationSource` for invalid user source when a located diagnostic is appropriate. Avoid `print`, which bypasses build-runner logging behavior.

## Dependency and language freshness

Do not embed speculative future language features or frozen dependency ranges in a reusable template. Read the target package constraints, resolve compatible current packages, and verify migration instructions against current changelogs. Dart macros were discontinued; any future alternative to part-based generation should be adopted only after it is supported by the target stable SDK and generator ecosystem.
