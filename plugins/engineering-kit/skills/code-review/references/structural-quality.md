# Structural Maintainability & Code-Judo Reference

Use this reference when auditing a diff, pull request, or branch for deep structural quality, maintainability regressions, spaghetti growth, file sprawl, or missed "code judo" simplifications. Ordinary reviews already check for over-abstraction and unit scope creep and must not skip those checks when this file stays unloaded.

## Core Standards

0. **Be ambitious about structural simplification ("Code Judo").**
   - Look for opportunities to reframe data shapes, types, or state ownership so whole branches, helpers, modes, conditionals, or layers disappear altogether.
   - Prefer solutions that delete complexity rather than rearranging or renaming it.
   - When a change adds incidental complexity where a cleaner reframing exists in the current architecture, flag the missed simplification directly.

1. **1,000-line file decomposition threshold (`S15`).**
   - Do not let a change push a file from under 1,000 lines to over 1,000 lines (or materially enlarge an already >1,000-line file) without decomposing cohesive responsibilities first.
   - Treat crossing 1,000 lines as a presumptive structural blocker unless there is a compelling reason and the resulting file remains clearly organized.

2. **No random spaghetti branching in existing flows (`S8`).**
   - Flag new ad-hoc conditionals, one-off boolean flags, nullable modes, or special-case branches bolted onto unrelated control flows.
   - Subordinate extraction to Rule 0 and `S7`: first look for a data/type reframing or early guard clause that deletes the branch; extract a dedicated state machine, dispatcher, or module only when it owns distinct state, a combinatorial test seam, or a layer boundary (never a one-caller pass-through wrapper).

3. **Prefer direct, boring, maintainable code over magic or thin indirection (`S7`).**
   - Flag thin wrappers, identity abstractions, and pass-through helpers that add indirection without clarifying the contract or isolating a real boundary.
   - Be skeptical of generic "magic" mechanisms that hide simple data-shape assumptions.

4. **Enforce explicit type and boundary contracts (`S5`, `S6`).**
   - Flag unnecessary casts (`any`, `unknown`), loosely-shaped ad-hoc objects, or silent fallback values that paper over unclear invariants on internal trusted paths.
   - Push for explicit typed models or boundary validation at the system edge so internal control flow stays direct.

5. **Keep logic in the canonical layer and reuse existing utilities (`S12`, `S13`).**
   - Call out feature-specific logic leaking into shared paths or implementation details leaking across package/layer boundaries.
   - Flag bespoke helpers when the repository already provides a canonical utility.

6. **Flag avoidable serial orchestration and non-atomic state updates.**
   - When independent async work is serialized for no reason and parallel execution is clearly simpler and safe, call it out.
   - When related state updates can leave state half-applied on failure, push for an atomic update structure.

7. **Enforce production tree hygiene (`S16`) and test authenticity (`S10`).**
   - Treat stray agent plans, walkthroughs, scratch notes, debug scripts, backup files, and `.context`/`.ws` artifacts committed into the repository tree as `P1` blockers (durable agent records belong in `~/.agents/projects/<project>/`).
   - Treat fake/hollow tests (asserting only on mocks, `toBeDefined()`, tautologies, weakened assertions, or leftover `.only`/`.skip`) as `P1`/`P2` blockers rather than valid test coverage.

## Priority Order for Structural Audits

When reporting structural maintainability findings, prioritize in this order:
1. Structural regressions and boundary leaks (`S13`)
2. Missed opportunities for code-judo simplification that delete whole branches or layers
3. Spaghetti / ad-hoc branching increases in shared or busy flows (`S8`)
4. Type-contract escapes, silent fallbacks, or thin wrapper indirection (`S5`, `S6`, `S7`)
5. File-size explosions crossing the 1,000-line decomposition threshold (`S15`)
6. Unnecessary serial orchestration or partial-state update hazards

Prefer a small number of high-conviction structural findings over a long list of cosmetic nits.
