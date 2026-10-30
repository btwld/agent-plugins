---
name: reference-implementation
description: >-
  Use when creating, reviewing, refactoring, or auditing a reference-quality implementation —
  canonical code that others should copy, where correctness, traceability, and earned
  abstraction matter. Trigger on "reference implementation", "canonical version",
  "golden-path example", "the blessed implementation", or auditing whether code deserves
  to be the reference. Not for ordinary bug fixes, cleanup, or optimization unless the
  result is meant to be authoritative or copied.
---

# Reference Implementation

Produce or audit canonical code: faithful to the agreed problem, easy to verify, and only
as abstract as the work requires. This is not ordinary review or cleanup. Use it when the
code is the authoritative example others should copy.

Whether you build, refactor, or only audit follows the user's authorization, not a mode.
Audit is read-only unless edits were requested. Do not infer permission to stage, commit,
push, merge, or publish. Preserve unrelated work. Recheck after the last authorized edit.

## Workflow

### 1. Establish intended behavior and authority

The source of truth is the authoritative spec, requirements, or accepted decisions — not
whatever the code currently does. Name only the material contract: inputs and outputs,
input preconditions and non-goals, boundary and error cases, order or ties, invariants,
and compatibility or operational/complexity limits that actually apply. Do not invent
missing policy. Respect stated exclusions; an out-of-contract case is not a missing
rule. Ask only when the answer would change the decision; label other assumptions
provisional rather than canonizing a guess.

Each meaningful rule has one authoritative definition. That does not mean one execution
site. Repeated enforcement can be correct at trust, persistence, or compatibility
boundaries; keep those sites traceable to the same rule and check that they agree.
Preserve checks needed at each boundary rather than centralizing execution merely to
remove repetition. Rule IDs or matrices are optional and useful only when they reduce
ambiguity.

### 2. Build or inspect the simplest faithful implementation

Trace representative callers to their effects. A layer earns its place through a distinct
responsibility, guarantee, safety property, ownership, lifecycle, or clearer verification.
Shape-only wrappers and same-shape conversions are often wasteful; a single caller is not
proof a layer is useless. Preserve useful boundaries even when they have one caller.
Simpler means less needless complexity, not the fewest lines.

Scale the writing: hold tiny work in a short reply; capture at-risk rules and tests in
plain notes for most work; reach for `templates/implementation_canvas.md` only when shared
notes materially help a large or collaborative case. The canvas is optional. Do not force
a redesign or a canvas onto already-clear canonical code.

### 3. Verify and challenge behavior and evidence

Tests come from the contract, not from copies of production logic or weakened
expectations. Cover examples, relevant boundaries, failures, and order or ties. Add a
small independent oracle, property, or metamorphic check only when it actually helps.

In a diff, distinguish mechanical or structural intent from evidenced preservation and
from explicit semantic changes. Do not treat formatting, moves, or renames as
behavior-preserving by definition; hidden semantic drift is not a refactor. A semantic
change updates the agreed contract, the implementation, and the tests together, with
authorization. Performance requirements in the contract remain in force; preferring
correctness does not waive them.

Challenge suspected findings against context and counterevidence. There is no finding
quota. Never claim tests that were not run. Name the exact snapshot that was tested, and
separate baseline failures from new regressions.

### 4. Report proportionately

Lead with a short outcome and evidence-backed `file:line` findings that exist. For an
audit, distinguish a demonstrated defect from inability to establish reference quality
because evidence is missing. Do not give an unconditional pass from source inspection
alone. A Pass/Fail label is optional; clearer plain wording is enough. For
implementation, say what behavior changed, which checks actually ran, and what remains
limited. Skip empty categories and rigid templates.
