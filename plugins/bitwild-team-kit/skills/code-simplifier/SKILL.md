---
name: code-simplifier
disable-model-invocation: true
description: >
  Use when the user explicitly invokes `$code-simplifier`, names the code-simplifier skill and asks
  to use it, or explicitly asks to deslop recently written or modified code. Do not infer it from a
  generic cleanup request or a non-trivial edit. Run a separate, behavior-preserving refinement and
  slop-removal pass over a user-selected code scope, defaulting to recently written or modified
  code. Do not use for larger structural work such as cross-module consolidation, responsibility
  splits, or replacing an architecture; handle those as scoped engineering changes with
  proportionate behavior-preservation tests.
---

# Code Simplifier

<!-- Derived from Anthropic's code-simplifier agent and modified by Leo Farias.
See ../../SOURCES.md. -->

Refine recently changed code so the behavior stays the same while the path from intent to effect
becomes easier to follow and free of generated code slop. Prefer direct, explicit code over clever
compression, speculative defensive guards, and layers that only rename or forward values.

Run this workflow only as an explicitly invoked pass (`$code-simplifier`, naming `code-simplifier`,
or an explicit request to deslop recent changes). Cleanup that is naturally part of an
implementation remains ordinary engineering work and does not require this skill.

## Establish the boundary

- Read the current diff or session edits, project instructions, formatter and linter configuration,
  nearby conventions, and the tests that protect the changed behavior.
- Use the scope the user selected; when none is stated, limit the pass to recently changed code.
- Treat surrounding code as evidence, not authority: preserve a pattern only while the
  responsibility that created it still exists.

## Refinement process

1. Trace each changed entry point through its important calls to the resulting output or effect.
2. Look for structural simplifications ("code judo") within the selected scope:
   - Reframe the local state model, data shape, or lookup table when doing so lets whole branches,
     one-off boolean flags, nullable modes, or helper layers disappear entirely.
   - Flatten deeply nested control flow with early returns, and eliminate scattered special-case
     `if` statements bolted onto busy flows or feature-specific logic leaking into shared paths.
   - Reuse existing canonical helpers in the codebase instead of keeping bespoke near-duplicates,
     and split out a focused helper or module when a diff pushes a file past a healthy size boundary
     (roughly 1,000 lines) by mixing distinct responsibilities.
3. Remove navigation-only hops: inline forwarding calls, collapse same-shape conversions, inline
   throwaway one-use variables returned on the next line, use a direct tear-off when signatures
   match, and keep repeated syntax when extracting it would only hide simple code.
4. Strip diff-level code slop while keeping real boundaries intact:
   - **Defensive bloat & silent fallbacks:** Remove impossible defensive checks, redundant null
     guards, blanket `try/catch` blocks, or silent fallback defaults (`?? ''`, `?? []`,
     `catch { return null }`) on trusted internal paths where declared types and narrowing already
     guarantee the state; keep error handling at IO, process, network, FFI, and user-input
     boundaries.
   - **Type escapes & suppressions:** Replace `any` casts, `unknown` casts, or unnecessary
     optionality used only to bypass type checking with the actual narrow type or explicit boundary
     validation. Fix the underlying local issue instead of leaving `@ts-ignore`, `@ts-expect-error`,
     `eslint-disable`, or `// ignore:` suppressions.
   - **Dead ceremony & generic naming:** Delete unused private helpers or single-value configuration
     knobs introduced in the diff, and replace generic placeholder names (`data`, `result`, `temp`,
     `item`, `processX`, `handleX`) with the domain terms used in neighboring files.
5. Enforce strict comment hygiene:
   - Delete comments that restate the code, tutorial/chat voice (`Note that...`, `Simply...`),
     task/PR history narration, section banners, and commented-out code.
   - **Reshape workaround sermons:** When a comment apologizes for or explains a confusing name,
     surprise, or awkward flow in in-scope code we own, rename or restructure the code so it is
     obvious without prose, then delete the comment.
   - Keep only comments that earn their place: legal/license headers, required public API contract
     docs, issue/RFC links, and `why` comments recording invariants, ordering constraints,
     ABI/protocol rules, or rejected alternatives forced by external systems we cannot reshape.
6. Run the narrowest formatting, analysis, and behavior tests that can prove the cleanup preserved
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

When the user requested an edit, apply the simplification and keep the final summary concise (1–3
sentences naming only material changes and verification). When the request was review-only, report
the concrete opportunities without editing.
