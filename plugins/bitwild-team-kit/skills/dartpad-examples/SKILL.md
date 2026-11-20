---
name: dartpad-examples
description: Use when creating, simplifying, documenting, or verifying self-contained Dart and Flutter examples for DartPad. Use for copy-paste teaching snippets and small interactive package showcases, including Mix examples; not for general application architecture.
disable-model-invocation: true
user-invocable: true
---

# DartPad Examples

Create examples that teach one recognizable idea, run from a single pasted file,
and expose the package's useful API without surrounding application machinery.
When revising an approved example, preserve its appearance and interaction unless
the user explicitly changes them.

## Establish the execution target

- Identify the concept, intended interaction, package, and DartPad channel.
- Check the package version supported by that DartPad channel. A repository's
  local package can expose APIs absent from the published package.
- Use local source to understand implementation, but the target published API is
  authoritative for snippet compatibility. Do not claim DartPad compatibility
  based only on local analysis, widget tests, or a native build.
- Keep the source self-contained: imports supported by the target, a runnable
  `main()`, and no project-relative files or undeclared assets.

## Design for teaching

- Lead with the visible effect, then choose the smallest implementation that
  makes that effect reliable. Review complexity against visible benefit, not
  line count alone.
- For styling showcases, put named style declarations outside `build()`, not
  merely above its return statement. Use top-level values for fixed styles and
  small functions with explicit inputs for state-dependent styles. In `build()`,
  obtain the styles and compose their callable widgets. Keep constraint- or
  context-dependent calculations in the scope that owns those inputs; avoid a
  style registry or helper class just to enforce this layout.
- Group explicit colors into a small local palette. Prefer role names for
  interchangeable colors, such as `trackOnColor`; a reused literal white can be
  `whiteColor`. Introduce tokens and themes only when they teach the concept or
  are genuinely required by the widgets.
- Choose a minimal app shell. `WidgetsApp` fits a custom Flutter-only control;
  Material widgets and integration can justify `MaterialApp`. The app `color`
  property does not paint its background; use a background widget as needed.
  Icons alone do not require MaterialApp. Check text metrics, TextField/Material
  ancestors, localization and overlays before removing the shell. Prefer explicit
  demo typography when small; retain a minimal Material shell when recreating its
  behavior would be more complex. A white background is a design choice, not a
  cleanup requirement.
- Avoid extra enums, factories, helper classes, and configurable parameters that
  merely rename one use. Keep geometry readable; name shared dimensions when
  doing so prevents inconsistent sizing, not to extract every literal.
- Removing drag behavior, keyboard support, semantics, or reduced-motion support
  is a behavior change, not a cleanup. Preserve existing behavior unless the
  requested teaching scope permits the change. If an explicitly motion-focused
  demo always animates, document that boundary briefly.

## Motion with a purpose

- Distinguish press acknowledgement from the state transition. For example,
  shrink on press, then move and deform on activation.
- Use an implicit spring for state-dependent position or scale. Use keyframes
  when even a quick activation must play a deliberate multi-stage sequence.
- Avoid adding several independent bounces for the same event. Keep the main
  movement dominant, settle promptly, and inspect the effect at its real size.
- For squash-and-stretch, inverse axis scaling can preserve area. Uniform
  scaling is a different effect; do not substitute it as a syntax cleanup.
- Check cancellation, repeated activation, and parent rebuilds. Separate the
  selected state from a one-shot animation trigger only when both are needed.
- Keep notifier/controller disposal. Do not add delayed callbacks by habit;
  verify whether the animation must wait for a rebuilt configuration. Remove
  scheduling only after testing the resulting animation, not just final state.

## Mix-specific guidance

Use the available Mix skill for API details and inspect the target package.
For DartPad, the deployed package version and the snippet's teaching scope take
precedence over local-only APIs or general application-level token guidance.

- Start ordinary declarations with concrete stylers and fluent chains.
- Use callable stylers when supported: `track(children: [travel(child: thumb())])`.
- Use contextual shorthand where the type is known. For example:
  `style.wrap(.scale(x: scale, y: 1 / scale))`. The leading member must actually
  be a constructor/static factory on the inferred type in the target version.
  For instance-only methods, start with `.new()`: Mix 2.1.0 supports
  `.onHovered(.new().wrap(.opacity(0.5)))`, not `.onHovered(.wrap(...))`.
  Preserve transform modifier order when shortening syntax.
- Keep `KeyframeTrack<double>` explicit when it clarifies the animated value.
  Read it with `values.get<double>('squish')`. One string ID does not justify an
  enum; use a shared constant if repeated IDs become a maintenance problem.
- A styler has one animation configuration: chaining `.animate()` and
  `.keyframeAnimation()` does not combine independent animations. Separate
  travel and shape widgets when both must animate independently.
- Preserve the intended accessibility role. In published Mix 2.1.0, `Pressable`
  provides button semantics and does not accept `semanticsRole`. For a custom
  switch, an outer `Semantics(label: ..., toggled: ..., onTap: ...)` with
  `Pressable(excludeFromSemantics: true, onPress: ...)` avoids the duplicate
  button role. Recheck the API for other versions. Apply the same role-ownership
  check to checkboxes (`checked`) and selections; ordinary buttons can retain
  Pressable semantics. Inspect the resulting semantics tree, not just wrapper
  properties. If visible child text already supplies the label, do not repeat
  it on the outer Semantics node; alternatively exclude the redundant child
  semantics. Assert the final merged label appears once. Report pre-existing
  role/action defects and repair them when in
  scope; preserving a defect is not proof of accessibility correctness.
- Do not assume zero-duration animation configs work in every Mix version.
  Where necessary, omit animation for an immediate state change and verify
  switching that behavior while an animation is running.

## Tutorial documentation

- Use Effective Dart-style `///` documentation for public functions and widgets:
  a concise summary sentence, then only the explanation a reader needs.
- Explain how to run the complete file and what to click, hold, or observe.
  Describe actual DartPad controls; do not invent a package-version selector.
- Use `[symbol]` links for relevant Dart identifiers and backticks for code.
- Use ordinary comments for non-obvious implementation reasons: independent
  animation layers, geometry relationships, trigger ownership, or semantics.
- Do not narrate every line, duplicate parameter names in prose, or add a long
  tutorial before a tiny example. Keep comments synchronized after refactors.

## Verify the actual deliverable

1. Format and analyze the snippet. Run focused behavioral tests for changed
   interactions; sample intermediate animation geometry as well as final state.
   When changing the app shell, scope or theme, also exercise the snippet's real
   `main()` without the gallery harness. Compare text metrics and appearance;
   inherited gallery dependencies can hide standalone failures.
2. Validate the exact final source with the target DartPad service or UI. When
   available, reuse the project's existing DartPad verifier. The stable service
   currently exposes `https://stable.api.dartpad.dev/api/v3`: `GET /version`,
   `POST /analyze`, and `POST /compileDDC`, with `{"source": "..."}` for POSTs.
   Treat endpoints as discoverable implementation details, not permanent APIs.
3. Inspect diagnostics and the compilation payload; HTTP success alone is not
   proof of successful compilation. If the service is unavailable, report the
   checks completed and the remaining DartPad verification gap.
4. Only send source intended for public DartPad use to that service. For private
   code not authorized for upload, validate in an isolated project pinned to
   the published dependency and report that this is not DartPad execution.
5. Preview when interaction or visuals changed. Verify the correct entry point
   and current source are running; launching a process or reopening a stale
   window is not visual verification.
6. If a gallery copies source from bundled assets, refresh its asset bundle
   before checking the copy action. When a user reports an error already fixed
   locally, compare the failing source and version instead of assuming the user
   is running the updated snippet.

Finish with the source location, the important simplifications, behavior changes
if any, and exactly which environments passed. Do not imply that compilation
proves runtime behavior or that local tests prove published-package compatibility.
