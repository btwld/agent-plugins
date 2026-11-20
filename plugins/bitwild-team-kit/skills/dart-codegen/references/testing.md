# Testing Dart Generators

Use the testing APIs resolved by the target repository. Add compatible dependencies with the SDK rather than copying frozen ranges:

```bash
dart pub add --dev build_test test
```

Use an additional golden package only when the repository already uses it or textual snapshots materially improve reviewability.

## Focused builder tests

`build_test.testBuilder` can provide in-memory assets and assert generated outputs. Adapt its signature to the installed `build_test` version:

```dart
await testBuilder(
  myBuilder(BuilderOptions.empty),
  {
    'example|lib/model.dart': source,
  },
  outputs: {
    'example|lib/model.my_builder.g.part': contains('generatedName'),
  },
);
```

Provide resolvable annotation and dependency sources. Prefer a small fixture package when reproducing the real resolver setup in memory becomes harder to understand than the behavior under test.

## Diagnostics

`source_gen` commonly reports invalid source through build logs rather than rethrowing `InvalidGenerationSource` to the test body. Check the behavior of the installed version and assert the diagnostic message and source location through its supported logging/test API.

A builder factory that validates `BuilderOptions` synchronously can be tested as an ordinary thrown error; do not assume generator-time and factory-time errors use the same channel.

## Evidence layers

Choose evidence that matches the risk:

- exact generated fragments for a small deterministic formatter;
- compilation or resolver tests for imports, generic types, nullability, and symbol collisions;
- diagnostic tests for unsupported element kinds and invalid annotation values;
- a multi-file or multi-package fixture for ordering and aggregation;
- an end-to-end `build_runner` invocation for registration, combining, and output locations.

Text goldens prove the rendered text. They do not prove that imports resolve or that the builder is activated correctly.

## Typical end-to-end checks

Use the repository's scripts when present. Otherwise a fixture may run:

```bash
dart test
dart run build_runner build --delete-conflicting-outputs
```

Use the deletion flag only when conflicting files are known generated outputs owned by the fixture or builder.

## Coverage choices

Cover behavior that the generator actually implements:

- representative valid input;
- each important invalid contract;
- generic/nullability/import behavior when types are inspected;
- deterministic option handling;
- phase or aggregation behavior when present.

Do not manufacture tests for generics, package splitting, or multi-stage output when the generator contract does not contain those features.
