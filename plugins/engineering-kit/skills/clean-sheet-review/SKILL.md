---
name: clean-sheet-review
description: >-
  Use when an existing plan, spec, API, architecture, or implementation should be reconsidered
  from its purpose and first principles: "from first principles", "take a step back", "if we built
  this today", "what should survive", or "rethink this without being bound by previous design
  decisions". Derive a fresh proposal from
  real requirements, compare it with the existing solution, and explain code, migration, and
  document impact. Return keep, refine, simplify, redesign, split, or stop. Prefer wild-code-review
  for defects within a fixed design, architecture for focused decisions or developing a chosen
  API contract, and ordinary execution for an already-approved refactor. Not for first-time
  product discovery or an unrequested rewrite.
---

# Clean-Sheet Solution Review

Reconsider an existing solution from the app's purpose, users, and required outcomes. Treat its
current shape as a hypothesis. Use the evidence learned from building it to propose the smallest
correct solution and judge whether changing to it is worthwhile.

## Confirm the scope

A meaningful solution must exist, and the user must have authorized reconsidering some part of its
scope, API, architecture, data model, or framing. Keep any fixed dimensions fixed. Clarify only when
uncertainty could change the recommendation or compatibility impact; otherwise state assumptions.
A request to refactor while preserving behavior does not by itself authorize reopening the contract.

- Use `wild-code-review` for defects, regressions, or missing tests within a fixed design.
- Use `architecture` for a focused technical decision, initial design decision, or details of a
  chosen API contract. A clean-sheet review can itself propose a design of any relevant size;
  multiple public surfaces do not require another skill.
- Use ordinary engineering execution for approved edits; `code-simplifier` remains an explicitly
  requested refinement pass. No sequence of skills or delegation is required.

## Establish purpose and real constraints

Read available requirements and relevant repository evidence. For implemented work, trace at least
one real consumer through its effects; caller workarounds often expose a mismatch the internals hide.
For a plan with no code, check scenarios, contracts, and acceptance criteria. Never imply inspection
or execution that did not happen.

Separate the required outcomes, users, non-goals, hard constraints, external commitments, observed
facts, assumptions, and current design choices. Scale this brief to the problem. "It is a library"
or "there is a registry" describes today's solution unless evidence makes it a requirement.
Do not turn an omitted detail into a defect or invent product purpose when it is unknown.

ADRs and prior decisions explain why the current solution exists; their choices do not automatically
constrain the proposal. Extract any still-binding obligation and test whether its original reason
still holds. Preserve the obligation while considering different ways to satisfy it. User constraints
and applicable repository operating instructions continue to govern your actions. Prior approval is
neither proof that a design is best today nor permission to violate a real external commitment.

## Derive the proposal, then compare

Reason from purpose and constraints before choosing which current types or layers to preserve.
Ask what you would build if every current requirement had been a day-one assumption rather than
bolted onto an earlier shape. Sketch the caller's ideal usage and core data structures first so
downstream control flow becomes obvious and special-case branching disappears. A short mental
cross-check is sufficient for an obviously sound small design; a substantial redesign needs an
explicit independent proposal (and, when the design space is open, 2–3 genuinely distinct options
including subtraction) before the current-to-proposed comparison.

Trace each proposed capability to an outcome or invariant. Challenge unnecessary concepts and
forwarding layers, but retain boundaries that own semantics, lifecycle, authority, failure behavior,
or external obligations. Screen candidate shapes against shallow pass-through wrappers, leaked
internals, temporal splits, split ownership, and leaving two ways to do one task. One caller, a
familiar pattern, fewer types, or a single universal primitive
is not sufficient evidence for a design decision. Do not manufacture novelty to justify the review.
Use an isolated subagent only when the user explicitly requests delegated or parallel review.

Compare the proposal with actual code, consumers, tests, and prior decisions. For material elements,
state keep / change / remove / add / defer and why. Distinguish correctness defects from preferences;
try to disprove suspected problems using counterevidence. Keep evidence that supports the current
solution, and revise assumptions if inspection reveals new facts.

Check functional correctness and relevant failure scenarios. Add concurrency, security, performance,
operational, and migration analysis only where they could change the decision. A premortem or an
alternative design is useful when it tests a material uncertainty, not as a required report section.

## Assess impact and recommend

Price implementation and transition costs alongside the benefit. Cover affected behavior, APIs,
stored data, callers, rollout/recovery, tests, and operational ownership only where applicable.
A cleaner target alone does not justify migrating to it; distinguish the design you would choose
from scratch from the action worth taking now.

Identify the inspected ADRs, specs, guides, and examples that would need amendment or supersession,
and the reason. If documents are unavailable, name the document category to inspect rather than
inventing identifiers. A recommendation proposes superseding a decision; it does not mark that
record superseded or imply user approval. Preserve the decision history when changes are authorized.

Give one verdict with a short reason:

- **Keep:** the solution fits the demonstrated need; ordinary implementation checks or optional
  hardening do not require a new design.
- **Refine:** a material contract or design gap needs a bounded correction.
- **Simplify:** reduce internal complexity while preserving the public contract.
- **Redesign:** change the public contract or fundamental design; name the migration impact.
- **Split:** distinct responsibilities or obligations justify separation.
- **Stop:** the capability lacks a sufficient need or cannot justify its cost.

For a requested revised spec, provide the relevant goals, non-goals, consumers, interface and data
contracts, invariants, errors, compatibility, acceptance criteria, and open decisions. Keep unresolved
choices visible; scope the work across turns when needed. Once a direction is chosen, `architecture`
can help resolve its detailed decisions, and `writing-plans` can turn settled requirements into tasks.
These are available next steps, not automatic handoffs.

## Report and authorization

Lead with the verdict and reason. For **Keep**, default to a short explanation of the demonstrated
fit and at most one verification condition; omit speculative hardening or redesign. If the user
requested a detailed comparison or document-impact analysis, include it even when the verdict is Keep.
For change, include the purpose, proposal, comparison, material impact, and uncertainty proportionally.

When the user asks to keep a review, save it at `~/.agents/projects/<project>/reviews/<yyyy-mm-dd>-<slug>.md`
using the shared project identity and provenance fields from `writing-plans` with `kind: review`, and
link supporting files under the matching `~/.agents/projects/<project>/evidence/<yyyy-mm-dd>-<slug>/`,
unless the user or repository instructions specify another location.

Default to review only. When edits are authorized, act within that scope, subtract dead or
superseded internal paths and migrate internal callers so old and new ways do not coexist without a
compatibility requirement, preserve unrelated work, verify changed and preserved behavior, and report
actual checks and compatibility effects. A review request does not authorize rewriting code or ADRs,
committing, pushing, merging, or publishing.
