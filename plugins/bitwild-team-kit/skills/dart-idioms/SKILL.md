---
name: dart-idioms
description: >
  Use when designing or reviewing Dart and Flutter APIs for idiomatic ownership,
  constructor and factory choices, redundant construction wrappers, static-only
  utility classes, extension placement, or resource lifecycle boundaries. Apply
  scoped simplifications when requested. Not a formatter, general Flutter
  architecture migration, or substitute for task-specific testing and tooling.
---

# Dart Idioms

Choose the simplest Dart construct that expresses the actual responsibility,
invariants, and lifecycle. Reduce indirection, not merely line count or the
number of factories and top-level functions.

## Establish ownership before syntax

Read project instructions, SDK constraints, exports, relevant callers, and tests.
A review request produces findings; an implementation request produces edits.
Stay within the selected scope. A focused question does not require a repository
audit. Preserve the established compatibility policy; a hard cutoff in one
project is not a default for other projects.

Trace what each candidate actually does: construct a value, enforce an invariant,
operate on owned state, convert representations, acquire a resource, or compose
collaborators. State the responsibility before choosing its declaration form.
A one-call wrapper can still protect policy, a public seam, or lifecycle ownership.

For exhaustive audits, use syntax-aware inspection to distinguish real constructors,
static methods, top-level functions, and extensions. Use an available Dart analyzer
or AST tool; text search finds candidates but does not prove their semantics.
Check call sites, constructor tear-offs, subclasses, and public exports. Exclude
generated files and deliberate fixture samples from edits unless they are in scope.

## Choose the construct

| Responsibility | Preferred starting point |
| --- | --- |
| Initialize fields and enforce one type's invariants | Unnamed generative constructor |
| Meaningful alternative initialization or direct field mapping | Named generative constructor, redirecting when appropriate |
| Select an implementation, reuse an instance, or compute substantial intermediate state | Factory constructor |
| Parse nested/untyped data or normalize coupled values | Named factory when its body makes the operation clearer |
| Operate on an object's state or behavior | Instance member |
| Compute an independent algorithm or convert across owners | Top-level function |
| Coordinate peers across layers or prepare application resources | Explicit orchestration function |
| Offer type-owned asynchronous loading/opening | Explicit async static operation or appropriately owned service/function |
| Open a synchronous resource owned by the returned type | Explicitly named operation, often a named factory |
| Add cohesive convenience to a type that cannot be changed | Extension, when its static dispatch and discoverability fit |

These are decision criteria, not a syntax quota. Factories need not return subtypes.
A readable factory can be better than a generative constructor supported by a
network of helper functions. Likewise, `fromMap` and `fromJson` are naming conventions,
not requirements to use a factory; simple decoding can fit a generative initializer.

### Construction and invariants

Move a wrapper whose sole responsibility is constructing one owned type to a real
constructor, or remove it and call an existing constructor directly. Do not merely
move the same wrapper to a static method, namespace class, or extension. Keep genuine
cross-layer adapters, conversions, asynchronous creation, and composition roots
where their dependencies belong; moving them onto a domain type can invert layering.

Inspect the declaration, not just the call syntax:

```dart
Entry.fromRecord(Record record) : key = record.key; // Named generative constructor.

factory Entry.fromMap(Map<String, Object?> map) {
  final decoded = decodeEntry(map);
  return Entry(key: decoded.key);
}

static Entry fromRecord(Record record) => Entry(key: record.key); // Not a constructor.
```

Put required invariants on every supported public construction path. A validating
`checked` constructor is not the invariant owner if the ordinary constructor can
bypass it. An unchecked path may be intentional for trusted internal reconstruction;
keep it private or explicitly justified by the public contract.

Use initializer helpers for simple normalization without hiding complex work in
them. Runtime input validation must not rely solely on assertions. Preserve error
types, nullability, evaluation order, immutability, identity/caching semantics, and
existing const use. A factory-to-generative conversion can affect subclassing,
super-constructor calls, and constructor tear-offs even when ordinary calls look
unchanged.

### Resource acquisition and orchestration

Dart constructors cannot be async. A `Future<T>` operation such as `T.open()` is
legitimate even though its declaration is static, not a constructor. Keep cleanup
on partial failure and make ownership and disposal clear.

Use names such as `open`, `load`, or `prepare` when work acquires resources or changes
external state. Constructing a value from an already loaded snapshot should not
claim to open a resource. Directory creation plus path resolution belongs to
preparation/orchestration, not an innocuous value constructor. Do not automatically
change synchronous behavior to asynchronous behavior: assess callers, error timing,
and the requested scope.

### Algorithms, utilities, and extensions

Keep independent functions top-level when no meaningful object owns them. A class
with only static members is not automatically a useful owner. Conversely, retain
a cohesive algorithm/configuration object or a type-owned identity calculation
when moving it would obscure its contract. Do not relocate solely to satisfy a
top-level-function or static-member ban.

Extensions are useful adaptations to external types, not a hiding place for
construction, I/O orchestration, or unrelated helpers. Account for import visibility
and static dispatch; they do not override runtime polymorphism.

## Flutter boundaries

Prefer const generative constructors for immutable widgets when their fields and
superclass allow them. Domain parsing factories remain ordinary Dart APIs.

Keep resource acquisition and persistent side effects out of widget construction
and `build()`. Use the existing lifecycle owner: State, controller, repository,
provider, or equivalent. Preserve initialization/update/disposal behavior; never
dispose a borrowed resource merely because an API moved.

Extract a widget when component identity, inherited dependencies, reuse, or a
rebuild boundary makes it useful. Do not mechanically replace every rendering
helper with a widget. Preserve keys, context semantics, and state retention.
Do not introduce a state-management framework as part of an idiom cleanup.

## Complete the requested change

For material decisions, explain what to keep, simplify, relocate, or remove and
why. Keep a per-declaration inventory only when an audit needs it. If the current
API is already direct and idiomatic, say so without inventing work.

Update affected callers, examples, and API/migration documentation. With an
authorized hard cutoff, remove obsolete entry points rather than adding aliases.
Otherwise honor the package's supported public contract.

Run the relevant formatter, analyzer, and behavior checks. Focus tests on changed
invariants, parsing, error behavior, resource cleanup, or widget lifecycle—not on
whether a declaration happens to contain the word `factory`. Check removed symbols
and separate skipped checks from passed checks.

When a language rule is uncertain, consult the applicable SDK documentation:
[Dart constructors](https://dart.dev/language/constructors),
[Effective Dart design](https://dart.dev/effective-dart/design), and
[Flutter build contract](https://api.flutter.dev/flutter/widgets/State/build.html).
Language constraints are authoritative; project conventions and the preferences
above do not turn one valid Dart form into a universally forbidden form.
