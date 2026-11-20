---
name: ack
description: >-
  Use when a Dart or Flutter project uses package:ack and needs to validate
  untrusted input, define a schema or bidirectional codec, generate an Ack
  model, import or export JSON Schema, or migrate between Ack versions.
  Also use when the user explicitly asks to adopt Ack for one of these tasks.
---

# Ack schema validation

Start at the caller. Identify the input the application receives, the Dart value it needs, and whether another consumer expects that value to encode back to a particular wire format.

## Match the project's version

Read the consuming package’s constraints and the workspace lockfile. Use `.dart_tool/package_config.json` to locate the resolved `ack` and, for generated models, `ack_generator` sources. For a Git or path override, read the guides from that checkout. For a hosted release, follow the matching tag’s `llms.txt`. When adding Ack to a new project, check SDK compatibility and respect the project's stable or prerelease policy. [Published releases](https://pub.dev/packages/ack/versions) · [Ack 1.7.1 guide index](https://github.com/btwld/ack/blob/v1.7.1/llms.txt) · [Ack 2.0.0-beta.3 guide index](https://github.com/btwld/ack/blob/v2.0.0-beta.3/llms.txt)

## Implement the boundary

- **Validate external input.** Define required fields and constraints with the fluent builders. Use `safeParse` when invalid input is an expected outcome. Branch on `isOk` or `isFail` before reading the value or error. Preserve the field-level error information the caller needs.
- **Model missing values deliberately.** Decide separately whether a field may be omitted, may contain JSON null, or needs a default. PATCH handlers commonly distinguish “leave unchanged” from “clear this field.” Check how the resolved version represents those two cases before mapping to a nullable Dart field.
- **Encode values sent elsewhere.** If parsing changes the type or representation, choose a bidirectional codec with an explicit encoding rule. Test the wire value produced by encoding. A one-way parse transform can be sufficient when the value stays inside the application.
- **Generate typed models.** Edit the annotated source and follow the resolved generator’s part-file convention. For example, 1.7.1 uses both `<file>.ack.dart` and `<file>.ack.g.dart`. The 2.0.0-beta.3 generator uses one `<file>.g.dart` and supports `JsonMaybe<T>` on a class field to preserve omitted, explicit-null, and populated values. Run `dart run build_runner build` from the consuming package and test the model’s parse and encode entry points. Generated constructors accept unchecked values.
- **Integrate a provider.** For JSON Schema interchange, confirm the consumer’s dialect and check a representative schema through the actual consumer. Use the version-matched guide for the specific adapter.

For example, this schema accepts an omitted delivery note, an explicit null, or a string. A quantity of zero fails at the boundary.

```dart
import 'package:ack/ack.dart';

final orderSchema = Ack.object({
  'quantity': Ack.integer().min(1),
  'note': Ack.string().optional().nullable(),
});

void main() {
  final result = orderSchema.safeParse({'quantity': 0});
  if (result.isFail) {
    final error = result.getError();
    if (error is SchemaNestedError) {
      for (final field in error.errors) {
        print(field.path);
      }
    } else {
      print(error.path);
    }
  }
}
```

Exercise a valid payload and the smallest invalid payload that demonstrates the rule. For a PATCH endpoint, also test omitted and explicit-null fields through the handler. For a codec or generated model, parse and encode a known input and compare the resulting wire payload. Run the project's analyzer and focused tests, and report which boundary they exercised.
