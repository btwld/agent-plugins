---
name: code-simplifier
description: >
  Use when the user explicitly invokes `$code-simplifier` or names the code-simplifier skill and
  asks to use it. Do not infer it from a generic cleanup request or a non-trivial edit. Run a
  separate, behavior-preserving refinement pass over a user-selected code scope, defaulting to
  recently written or modified code. Do not use for
  larger structural work such as cross-module consolidation, responsibility splits, or replacing an
  architecture; handle those as scoped engineering changes with proportionate behavior-preservation
  tests.
---

# Code Simplifier

<!-- Derived from Anthropic's code-simplifier agent and modified by Leo Farias.
See ../../SOURCES.md. -->

Refine recently changed code so the behavior stays the same while the path from intent to effect
becomes easier to follow. Prefer direct, explicit code over both clever compression and layers that
only rename or forward values.

Run this workflow only as an explicitly invoked pass. Cleanup that is naturally part of an
implementation remains ordinary engineering work and does not require this skill.

## Establish the boundary

- Read the current diff or session edits, project instructions, formatter and linter configuration,
  nearby conventions, and the tests that protect the changed behavior.
- Use the scope the user selected; when none is stated, limit the pass to recently changed code.
- Treat surrounding code as evidence, not authority: preserve a pattern only while the
  responsibility that created it still exists.

## Refinement process

1. Trace each changed entry point through its important calls to the resulting output or effect.
2. For each material new layer on those paths, identify the distinct responsibility it owns; scale
   the inspection to the change rather than cataloging every local declaration.
3. Remove navigation-only hops: inline forwarding calls, collapse same-shape conversions, use a
   direct tear-off when signatures match, and keep repeated syntax when extracting it would only
   hide simple code.
4. Re-read the simplified path for naming, control flow, nesting, comments, and project consistency.
5. Run the narrowest formatting, analysis, and behavior tests that can prove the cleanup preserved
   the contract.

## What earns a separate layer

Keep a boundary when it protects an invariant, changes ownership, validates or normalizes input,
owns a distinct phase or lifecycle, isolates an external system, provides a deliberate public or
test seam, or removes duplicated meaning. A single caller is a prompt to inspect a layer, not an
automatic deletion rule.

A layer is suspect when it only:

- forwards the same arguments to one callee;
- copies fields between equivalent representations;
- adapts a callback and then delegates to another one-use helper;
- groups code under a vague name without hiding complexity; or
- anticipates reuse or extensibility that has no demonstrated consumer.

Do not replace a shallow function with a namespace class, factory, extension type, or other shape
unless that shape owns a real responsibility. The goal is fewer concepts and cognitive hops, not a
preferred artifact type or the fewest lines.

## Preserve clarity and behavior

- Keep failure behavior, ordering, async semantics, ownership, public compatibility, and observable
  output unchanged unless the user separately authorizes a behavior change.
- Do not merge unrelated concerns, expose raw formats to more callers, remove useful names, or turn
  readable branches into dense expressions.
- Use the project's language conventions. If the cleanup depends on a language-specific design
  choice, verify it against the applicable language guidance rather than relying on generic style
  folklore.

When the user requested an edit, apply the simplification and report only material changes and
verification. When the request was review-only, report the concrete opportunities without editing.
