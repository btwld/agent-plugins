---
name: clean-sheet-review
description: >-
  Use when a plan, spec, API, architecture, or implementation already exists and the user wants it
  re-examined from a clean sheet — a fresh-eyes redo that may reconsider scope, public API,
  dependencies, or whether the artifact should exist at all. Trigger on "if you built this again,
  how would you do it" or "what would you simplify or replace now that it's built". Returns one
  sized verdict: keep, refine, simplify, redesign, split, or stop. Prefer native diff review for routine
  PR bug-finding and architecture or native system modeling for first-time design. Not for approved edits
  whose scope and design are fixed.
---

# Clean-Sheet Solution Review

Re-evaluate an existing plan, spec, API, architecture, or implementation from a clean sheet. Keep the facts and real constraints learned so far, but treat the current scope and design as provisional, and return the smallest correct solution plus a justified verdict.

This is a deliberate second pass, not a routine line-by-line code review. Its job is to counter attachment to the first design — the sunk-cost pull of "we already built it" — while still respecting the evidence that building it produced.

## Scope after activation

Use this skill only when a meaningful solution already exists **and** the user has given permission to reconsider at least one of scope, public API, architecture, data model, or problem framing. When that permission is ambiguous, clarify it rather than assuming a rewrite is wanted.

Do not turn a normal review into a redesign. Hand off instead when:

- Scope, behavior, and API are fixed and the user wants bug, regression, or risk findings -> native diff review.
- No prior solution exists yet and the user wants a first design -> `architecture` for a decision/ADR or native system modeling for a broader system.
- Scope and design are fixed and the user already wants the edit implemented -> use ordinary
  engineering execution; use `code-simplifier` only when the user explicitly invokes it as a
  separate cleanup pass.
- The user wants a single-axis audit (security-only, performance-only, accessibility-only) and has not asked to reopen the design.

## What you're working with

Pick the mode from what you actually have; the mode changes the evidence available, not the standard:

- **Plan mode:** a plan or spec exists, no code yet. Test it for internal consistency, missing behavior, undefined terms, and unverifiable acceptance criteria.
- **Implementation mode:** working or partial code and tests exist. Trace requirements to real code paths and run what you safely can.
- **Combined mode:** plan plus implementation plus the lessons from building it — the richest evidence.

Use any evidence available: the decisions so far, the current plan or design notes, source/tests/schemas/config/docs, a branch or diff, observed failures or user feedback, and hard constraints (compatibility, migration, schedule, security, cost, platform). When you can read the repo, inspect the artifacts before concluding — verified evidence is the whole point of a second pass, so do not infer what you can check directly. Treat details omitted from a short prompt as unknown, not as defects in the existing design.

## The core moves

Every clean-sheet review, whatever its size, does four things:

1. **Separate requirements from design choices.** Do not let "we built it as a library / service / registry / schema" masquerade as a requirement — naming the artifact is often where the first design quietly over-committed. An unspecified dimension is reconsiderable unless changing it breaks a clear external commitment.
2. **Judge the current design on evidence, not attachment.** Inspect what is actually there; keep correctness defects separate from maintainability preferences; and evaluate each decision against the information that existed when it was made rather than criticizing prior authors. Missing evidence can justify a verification question, but it does not prove a defect.
3. **Return one clear verdict with a brief reason** — typically **keep**, **refine**, **simplify**, **redesign**, **split**, or **stop**. Say the primary reason, the most important tradeoff, and what of the current approach survives. Use **keep** when the stated mechanism fits the demonstrated requirements and only normal implementation checks remain. Use **refine** only when evidence shows a material gap that changes the design or contract. Optional hardening, another valid implementation, or a new requirement introduced by the review does not change **keep** to **refine**.
4. **Price the change.** A redesign must clear its combined implementation-and-migration cost — "cleaner" alone does not justify a rewrite. Keep is a valid and common answer; never recommend a rewrite just because a review was requested. Backward compatibility is not automatically a wall — verify whether it is a hard constraint or a migration cost before treating it as one.

## Optional techniques — reach for what the problem needs

Scale the second pass to the artifact. A sound design heading for **Keep** needs almost none of these; a "rewrite the reporting service" needs most. Use a technique when it changes the call, not by default.

- **Neutral problem brief** — rewrite the problem without the current solution, classifying each item as required outcome / hard constraint / external commitment / observed evidence / current design choice / assumption / unknown. Use it when requirements and design choices are tangled; it is the sharpest tool for move 1.
- **Independent clean-sheet design** — when heading toward simplify or redesign, design from the
  brief rather than by editing the current architecture. Write the independent design before
  comparing it with the current one. Use an isolated subagent only when the user explicitly asks
  for delegated or parallel review. Aim for the narrowest useful scope and interface that covers
  demonstrated needs. Describe responsibilities and data flow before choosing artifact names, so
  the new design does not merely replace one set of layers with another.
- **Subtraction pass** — trace the shortest path from each requirement to its outcome through both
  designs. For every concept, representation, conversion, delegation hop, extension point, and
  public surface, ask what requirement, invariant, or proven use would fail if it disappeared.
  Collapse anything whose removal changes only navigation or syntax; keep a boundary when it owns
  distinct semantics, lifecycle, authority, failure behavior, or an external commitment.
- **Premortem** — assume it shipped and later failed; name the material plausible causes, the
  earliest signal each produces, and a prevention/detection/containment measure. Use it only when
  it could change the verdict, and do not invent unlikely risks to justify extra architecture.
- **Correctness & failure-mode sweep** — cover functional correctness always; other dimensions (invariants, boundary/partial/duplicate inputs, error recovery and idempotency, data ownership and migration, concurrency, security boundaries, performance limits, compatibility, testability) only where evidence makes them relevant to the verdict. Turn vague quality claims into concrete scenarios — replace "must scale" with a workload, an environment, and a measurable limit. Do not expand a compact design summary into a full hardening review unless the user asks for one.
- **Current-to-proposed comparison** — assign each material element an action: keep / change / remove / add / defer.
- **Revised specification** — only when the user asks: problem, goals, non-goals, consumers, core concepts and invariants, inputs/outputs, public interface, required behavior including errors and edge cases, data/file format, compatibility and migration rules, acceptance tests, and deferred capabilities — each public operation tracing to a use case or invariant. Then state which prior decision is superseded and why.

## Output

Return Markdown. Lead with the verdict and a short reason, then include only the sections the verdict needs. For **keep**, use exactly this compact shape and stop at 120 words:

```markdown
**Verdict: Keep.** <Why the demonstrated invariants are sufficient.>

- **Verify:** <The one condition that could overturn the verdict, or "No material condition remains.">
```

Do not add a hardening list, alternative design, revised specification, or implementation advice unless the user asks for it.

Include, proportionally, the verdict; a neutral reframe; what should survive; correctness defects and
design preferences kept distinct; and any assumption that could change the decision. Add a proposal,
comparison, or migration path only when the verdict needs it, and a revised specification only when
the user asks for one.

## Clarifying question policy

Ask only for missing facts that could invert the recommendation or change safety, compatibility, or
output structure — for example, whether a published API may break or stored data must stay readable.
Batch the material questions into one concise request when practical. Otherwise proceed on stated
assumptions and say how the recommendation would change if they are wrong.

## Review-only by default

Default to review only — do not modify files, APIs, data, or external systems. When the user explicitly asks you to implement: complete the review and lock the verdict first, convert the chosen direction into the smallest change sequence, apply only those changes, add or update tests that show both corrected and preserved behavior, run the relevant validation, and report what changed and the compatibility impact honestly. Never silently ship a breaking redesign when the user asked only for analysis.
