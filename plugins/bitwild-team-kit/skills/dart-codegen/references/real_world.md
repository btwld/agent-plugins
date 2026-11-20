# Generator Architecture Case Studies

Use established packages as evidence for tradeoffs, not as templates to copy. Inspect the current source and release used by the target repository because these projects evolve.

## `json_serializable`

Useful when evaluating annotation-driven, per-library helpers contributed to a combined part. Its current source can illustrate `GeneratorForAnnotation`, shared-part output, configuration layering, and specialized type helpers.

Question to carry forward: does the new generator have the same per-element output shape, or is the resemblance only that both use annotations?

## `freezed`

Useful when output needs a dedicated part and several declarations or constructors must be considered together. It demonstrates that a generator can use custom parsing and templates when `GeneratorForAnnotation` is too narrow.

Question to carry forward: does the output require whole-library coherence and private access, or would a smaller generator suffice?

## Riverpod generator

Useful for studying output selected from analyzer types and the coordination of several generated declarations. Verify its current builder and parser base rather than relying on an older class name.

Question to carry forward: is return-type inference part of the intended public contract, and are diagnostics clear when inference fails?

## `injectable`

Useful for studying multi-stage discovery and dependency-graph validation. Its exact intermediate assets, builder application, and aggregation scope are implementation choices, not a universal DI or registry pattern.

Question to carry forward: is repository-wide discovery genuinely required, and has package-boundary behavior been proven in a fixture?

## `auto_route`

Useful for studying an explicit user-declared root from which the analyzer follows referenced route types. A declared root can avoid implicit filesystem discovery.

Question to carry forward: can users express the aggregation root directly and receive better diagnostics as a result?

## Drift generators

Useful for comparing part output with more modular standalone output and for generators that consume Dart plus another source language. Inspect the selected Drift mode and version before generalizing from it.

Question to carry forward: does generated size, import ownership, or non-Dart input justify a different output mode?

## Selection rule

Choose from the target generator's input, output, privacy, import, aggregation, and distribution requirements. The popularity of a package does not make its architecture the default for an unrelated generator.
