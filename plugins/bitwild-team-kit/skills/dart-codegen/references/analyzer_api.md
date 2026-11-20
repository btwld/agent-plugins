# Analyzer and source_gen APIs

Analyzer element APIs and `source_gen` adapters are version-sensitive. Inspect the target package lockfile and current package API documentation before copying an example.

## Walking elements

Current element models expose declarations through the resolved library and class elements, but names can change between analyzer releases:

```dart
final library = await buildStep.inputLibrary;

for (final classElement in library.classes) {
  for (final field in classElement.fields) {
    // Inspect field.type and other properties supported by this analyzer.
  }
}
```

When migrating, use the analyzer's current element-model migration guide and compiler errors as the source of truth. Do not assume a suffix such as `element2` remains current merely because an older migration used it.

## TypeChecker

Current `source_gen` provides named-type constructors:

```dart
const annotationChecker = TypeChecker.typeNamed(
  AutoLabel,
  inPackage: 'auto_label_annotation',
);

const listChecker = TypeChecker.typeNamedLiterally('List', inSdk: true);
```

Use `TypeChecker.fromStatic` when a resolved `DartType` is already available. `TypeChecker.fromRuntime` was removed in `source_gen` 4.0.

`TypeChecker.fromUrl('package:pkg/file.dart#Type')` still exists, but current package documentation describes URL matching as brittle because library exports can move without changing the public type. Use it only when binding to that exact library URI is intentional.

See the current [TypeChecker API](https://pub.dev/documentation/source_gen/latest/source_gen/TypeChecker-class.html).

## Reading annotation values

`GeneratorForAnnotation.generateForAnnotatedElement` supplies a `ConstantReader`:

```dart
final name = annotation.read('name').stringValue;
final timeout = annotation.peek('timeout')?.intValue ?? 30;
final type = annotation.read('type').typeValue;
```

Use `read` for required fields and `peek` for optional fields. Validate the element kind and annotation values when the generator's contract requires it:

```dart
if (element is! ClassElement) {
  throw InvalidGenerationSource(
    '@AutoLabel can only annotate classes.',
    element: element,
  );
}
```

Returning no output is appropriate when an element is intentionally ignored. Do not turn every non-match into an error.

## Generator skeleton

```dart
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

Builder autoLabelBuilder(BuilderOptions options) =>
    SharedPartBuilder([AutoLabelGenerator()], 'auto_label');
```

Current `source_gen` part and library builders format their assembled output by default using the input library's effective language version. Add a manual `DartFormatter` only for a raw builder or when deliberately overriding the builder's `formatOutput` behavior.

## Analyzer types and emitted references

An analyzer `DartType` is not a `code_builder` `Reference`. Preserve generic arguments, nullability, and a library URI only when the emitter can use that URI.

- A standalone `LibraryBuilder` can use URL-bearing references with `DartEmitter.scoped()` to allocate imports.
- A part file cannot declare imports. Emit unprefixed references that the owning library already makes available, or change the output design if the part needs independent imports.

Handle the specific `DartType` forms required by the generator and test them. A catch-all based on `getDisplayString()` can lose import identity or produce code that only happens to compile in the fixture.

## Asset identity

Use the resolver when the source asset for an element is needed:

```dart
final assetId = await buildStep.resolver.assetIdForElement(element);
```

Prefer resolver APIs over reconstructing package paths from source strings.
