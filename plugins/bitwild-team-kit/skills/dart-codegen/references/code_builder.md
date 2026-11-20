# code_builder Usage

`code_builder` is useful when generated declarations and imports vary significantly. Its fluent builders are the package API, but using that API does not require adding builder wrappers or a builder-based architecture to the generated public surface.

For fixed boilerplate with a few substitutions, a readable template can be simpler. Test and format either approach.

## Constructing declarations

```dart
final generatedClass = Class((builder) => builder
  ..name = 'UserAdapter'
  ..fields.add(
    Field((field) => field
      ..name = 'id'
      ..modifier = FieldModifier.final$
      ..type = refer('String')),
  )
  ..constructors.add(
    Constructor((constructor) => constructor
      ..requiredParameters.add(
        Parameter((parameter) => parameter
          ..name = 'id'
          ..toThis = true),
      )),
  ));
```

Use `refer(symbol, url)` for a named external type and `TypeReference` for generics, nullability, bounds, and other structured types.

## Standalone libraries

A standalone generated library can own imports:

```dart
final library = Library((builder) => builder.body.add(generatedClass));
final emitter = DartEmitter.scoped(
  orderDirectives: true,
  useNullSafetySyntax: true,
);

final source = library.accept(emitter).toString();
```

`DartEmitter.scoped()` uses an allocator to create and prefix imports. Use `Code.scope` when a raw code fragment contains an external reference that must participate in allocation.

If a raw builder writes this output, format it with a `DartFormatter` configured for the target language version before writing the asset. Current `source_gen` `LibraryBuilder` formats output by default, so do not add a redundant formatting pass without checking its configuration.

## Part output

Part files cannot contain imports. Do not emit a standalone `Library` with scoped imports into a `SharedPartBuilder` or `PartBuilder` result. Use an unscoped emitter for declaration fragments and ensure referenced types are visible from the owning library:

```dart
final emitter = DartEmitter(useNullSafetySyntax: true);
final source = generatedClass.accept(emitter).toString();
```

If generated code fundamentally needs imports that the owning source library should not expose, use a standalone library design.

## Expressions and raw code

Prefer structured expressions when they improve import safety or escaping. Raw `Code` is reasonable for small statements whose text is clearer than a large expression-builder chain. Do not translate simple Dart into deeply nested fluent calls solely for consistency.

## Verification

Compile generated fixtures that exercise:

- two referenced libraries containing the same symbol name;
- nested generic and nullable types;
- part output whose owning library provides required imports;
- standalone output with allocated import prefixes.

Golden text tests are useful for readability, but compilation or resolver tests prove that imports and types are valid.
