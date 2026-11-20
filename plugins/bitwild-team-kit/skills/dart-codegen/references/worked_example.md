# Worked Example: Internal Shared-Part Generator

This example is intentionally one package because the annotation and generator are internal to one repository. Split the annotation API into a runtime package only when consumers or release ownership require that boundary.

The requested output contributes a helper to the user's combined `.g.dart`, so the example uses `SharedPartBuilder`. Do not adapt it to a standalone-library requirement without changing the builder design.

## Add compatible dependencies

From the generator package, use the target SDK to resolve current compatible versions:

```bash
dart pub add analyzer build source_gen
dart pub add --dev build_runner build_test test
```

If output becomes structurally dynamic or needs standalone import allocation, add `code_builder`. This simple fixed helper does not need it.

## Annotation

`lib/auto_label.dart`:

```dart
library;

class AutoLabel {
  const AutoLabel();
}
```

## Generator

`lib/src/auto_label_generator.dart`:

```dart
import 'package:analyzer/dart/element/element.dart';
import 'package:build/build.dart';
import 'package:source_gen/source_gen.dart';

import '../auto_label.dart';

class AutoLabelGenerator extends GeneratorForAnnotation<AutoLabel> {
  @override
  String generateForAnnotatedElement(
    Element element,
    ConstantReader annotation,
    BuildStep buildStep,
  ) {
    if (element is! ClassElement) {
      throw InvalidGenerationSource(
        '@AutoLabel can only annotate classes.',
        element: element,
      );
    }

    return "String get \$${element.name}Label => '${element.name}';";
  }
}
```

The returned source is a declaration fragment. Current `source_gen` builders assemble and format part output using the input library's effective language version.

## Builder factory

`lib/builder.dart`:

```dart
import 'package:build/build.dart';
import 'package:source_gen/source_gen.dart';

import 'src/auto_label_generator.dart';

Builder autoLabelBuilder(BuilderOptions options) =>
    SharedPartBuilder([AutoLabelGenerator()], 'auto_label');
```

## Builder configuration

`build.yaml`:

```yaml
builders:
  auto_label:
    import: "package:auto_label/builder.dart"
    builder_factories: ["autoLabelBuilder"]
    build_extensions: {".dart": [".auto_label.g.part"]}
    auto_apply: dependents
    build_to: cache
    applies_builders: ["source_gen|combining_builder"]
```

The declared `.auto_label.g.part` output agrees with the `partId` passed to `SharedPartBuilder`. The combining builder produces the user's `.g.dart`.

## Consumer source

```dart
import 'package:auto_label/auto_label.dart';

part 'user.g.dart';

@AutoLabel()
class User {}

void main() {
  print($UserLabel);
}
```

## Focused tests

Use `build_test.testBuilder` with a resolved annotation library and an input containing `part 'user.g.dart'`. Verify:

- a class produces `String get $UserLabel` in `user.auto_label.g.part`;
- an unsupported annotated declaration reports `InvalidGenerationSource` at that element;
- the example package compiles after the combining builder creates `user.g.dart`.

Exact `build_test` helpers and analyzer element APIs are version-sensitive. Copy the setup pattern from tests using the same installed `build_test`/`source_gen` versions rather than freezing a dependency-era fixture here.

## End-to-end check

```bash
dart test
dart run build_runner build --delete-conflicting-outputs
dart run lib/user.dart
```

Run the build command in a fixture/example package and use `--delete-conflicting-outputs` only where those conflicting files are known generated output.
