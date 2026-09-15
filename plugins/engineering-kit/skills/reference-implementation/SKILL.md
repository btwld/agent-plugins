---
name: reference-implementation
description: >-
  Use when creating, reviewing, refactoring, or auditing a reference-quality implementation —
  canonical code where correctness, traceability, and appropriate abstraction matter more than raw
  performance. Trigger on "reference implementation", "canonical version", "golden-path example",
  "the blessed implementation", or auditing whether code deserves to be the reference. Not for
  ordinary bug fixes, cleanup, or optimization unless the result is meant to be authoritative or
  copied.
---

# Reference Implementation

Produce or audit **reference-quality code**: code that preserves the problem's semantics, is easy to verify, uses only abstractions that earn their place, and is no more complex than the task requires. What separates this from ordinary review or refactoring is one discipline — the code must not invent semantics. Every meaningful behavior should trace to one authoritative rule and be tested at the behavior level.

## The core discipline

Whatever the size of the work, five things make code reference quality:

1. **Explicit semantics.** State inputs, outputs, definitions, boundary conventions, tie-breaking, edge behavior, non-goals, and any required complexity. If the code handles a case the semantics don't describe, either the code is wrong or the semantics are incomplete.
2. **One authoritative owner per meaningful rule.** Each behavior that could be misunderstood,
   duplicated, or changed has one authoritative definition. Repeated enforcement can be correct at
   independent trust, compatibility, or persistence boundaries; keep those sites traceable to the
   same rule and test that they agree. Repeated syntax is fine; independently redefined *meaning*
   drifts. Naming rules (R-001, ...) helps mainly across multiple files or owners, where they become
   searchable cross-references — it is optional in single-file work.
3. **Abstractions that pay rent.** Trace each named layer from its callers to the behavior it
   ultimately performs, and state the distinct responsibility it owns. Keep it when it names a
   problem concept, protects an invariant, owns a real phase or boundary, removes duplicated
   meaning, or makes verification easier. A forwarding call or same-shape representation change
   does not become meaningful merely because it has a type or function name. Abstract meaning,
   not shape.
4. **Real boundaries only.** Separate work when assumptions, guarantees, failure behavior, ownership,
   or side effects materially change. A conceptual step in an explanation does not require its own
   function, type, or phase in code.
5. **Behavior-level tests.** Tests should fail when behavior is wrong, not when internals are reorganized. Prefer golden examples, edge and boundary/tie cases, and rule- and invariant-level tests; add brute-force oracle, property, or metamorphic tests where the input space makes them feasible.

## Size the artifact to the work

The point is to make semantics explicit enough to prevent drift — not to produce a document. Scale accordingly:

- **Tiny:** hold it in your head or a short reply. Name the semantic rule, implement it once, test the edge case, resist abstractions that don't protect meaning.
- **Most work:** capture the at-risk semantics, the important rules and their one owner each, and the test plan in plain notes. Skip data-model and algorithm bookkeeping unless a type carries a non-obvious invariant or a real algorithm is in play.
- **Large or collaborative:** use `templates/implementation_canvas.md` as optional shared notes,
  keeping only the sections that clarify semantics, ownership, boundaries, or verification.

The canvas is an optional tool for the last case, not a required deliverable. Reach for it when the rule set, data model, or handoffs are complex enough that a shared artifact is what keeps the semantics from drifting.

## Auditing for reference quality

When judging whether existing code (or a refactor) deserves to be canonical, work from semantics outward:

1. **Reconstruct the intended semantics.** Inputs, outputs, boundary conventions, tie-breaking, edge behavior, non-goals. If you cannot find them, that itself is a drift risk — flag it.
2. **Check rule ownership.** Each important rule should have one authoritative owner and
   behavior-level tests. Distinguish independently redefined meaning from deliberate enforcement at
   multiple boundaries. Flag undocumented behavior, divergent rule copies, and broad integration
   tests standing in for missing rule-level coverage.
3. **Check real boundaries.** Where the implementation has a genuine parse, validation, core,
   persistence, or formatting boundary, verify that its assumptions and guarantees do not leak.
   Do not demand separate phases when a direct flow is clearer.
4. **Trace the implementation path.** Follow representative entry points to their effects or
   outputs. For every function, type, and representation change on that path, identify its owned
   responsibility. Flag navigation-only forwarding and parallel representations that do not
   change semantics, invariants, ownership, lifecycle, or authority. A single caller is a reason
   to inspect a layer, not by itself a reason to delete it.
5. **Check tests.** They should exercise behavior, not implementation structure.
6. **For a diff, classify each change** as mechanical (formatting/rename), structural (moved logic, same semantics), or semantic (changed output, edge behavior, validation, ordering, tie-breaking, or assumptions). No semantic change may hide inside a refactor.

Lead with a **Pass**, **Pass with issues**, or **Fail** verdict backed by `file:line` evidence.
Organize the rest around the issues that actually exist—correctness, drift, abstraction, missing
behavior, or tests—and omit empty categories rather than filling a fixed report template.

## When semantics change

A semantic change — different output, edge behavior, validation, tie-breaking, ordering, boundary convention, or algorithmic assumption — must update the semantics, the code, and the tests together. Mechanical and structural changes preserve behavior by definition; only semantic changes touch the rules, so keep them visible rather than buried in a refactor.

## Supporting files

Load only what the current task needs:

- `templates/implementation_canvas.md` — optional working notes for large or collaborative
  implementations; remove irrelevant sections rather than filling them mechanically.
