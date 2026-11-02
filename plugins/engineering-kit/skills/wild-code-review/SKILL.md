---
name: wild-code-review
description: >
  Use when reviewing or auditing a pull request, commit, diff, staged snapshot,
  working tree, pasted patch, files, or repository for defects, regressions,
  missing tests, suspicious or unnecessary code, hollow tests, stray
  non-production or planning artifacts, AI-generated code slop, structural
  maintainability, or adversarial keep/reject change verdicts. Do not use to
  implement features, author a pull request, redesign a system, or declare a
  canonical implementation.
---

# Wild Code Review

One review. Every pass considers correctness, suspicious or unnecessary code,
and hollow or tautological tests, then skeptically challenges both the change
and each suspected finding. Depth scales with scope and risk. A user-narrowed
scope still governs. Do not start this skill after every implementation;
ordinary review language is enough.

Neighboring owners stay separate: do not implement features, author
a PR ([pr-authoring](../pr-authoring/SKILL.md)), redesign
whether something should exist ([clean-sheet-review](../clean-sheet-review/SKILL.md)),
or audit a canonical example ([reference-implementation](../reference-implementation/SKILL.md)).
`code-simplifier` stays separately invoked.

## Review

1. Pin the target and constraints. Name the exact snapshot: commit, range, PR,
   staged index, working tree, or pasted snippet. Do not mix dirty-tree files
   into a commit or staged review.

2. Inspect the relevant code, callers, tests, and stated contracts. Work inline
   in a single fast pass by default; use at most 2–3 focused parallel lenses
   (correctness, tests/hygiene, structure/slop) only on large diffs when
   delegation is permitted and useful, avoiding multi-wave ceremony.

3. Check in priority order:
   - **Bugs, regressions, and contracts (highest priority):** observable
     behavior, error handling, ordering/concurrency, security boundaries, and
     swallowed failures.
   - **Test authenticity and repo hygiene:** changed or removed assertions;
     hollow or tautological tests, mock-only assertions, or `.only`/`.skip`
     leaks; and stray non-production files, agent plans, walkthroughs, or debug
     artifacts committed into the repository tree instead of
     `~/.agents/projects/<project>/`. A test that moves with the implementation
     needs independent contract support.
   - **AI slop and structural quality:** unjustified guards or impossible
     defensive checks on trusted internal paths; unnecessary abstractions or
     single-caller pass-through wrappers; ad-hoc spaghetti branching; files
     pushed past 1,000 lines without decomposition; missed code-judo data/state
     reframings that delete whole branches or layers; and misleading or
     restating prose only where demonstrably harmful. Do not infer AI authorship.
     Do not flag style, one-caller helpers, documentation, or catches by
     appearance alone.

4. Try to disprove each suspected finding against docs, types, callers, and
   other counterevidence. Distinguish defects, risk, and missing evidence.
   For concurrency or race risks that a single test run may not trigger,
   disprove by showing the interleaving is impossible or already synchronized.
   Clean code can produce no findings. Skeptical does not mean reflexively
   rejecting.

5. Run only focused, safe checks against the named baseline. Inspect unfamiliar code and build scripts before executing them. Isolate execution.
   Do not invent runs. A pre-existing failing test is not evidence that this
   change is wrong unless you show the change caused it.

## Report

When the user asks to keep a review, save it at `~/.agents/projects/<project>/reviews/<yyyy-mm-dd>-<slug>.md` using the shared project identity and provenance fields from `writing-plans` with `kind: review`, and link supporting files under the matching `~/.agents/projects/<project>/evidence/<yyyy-mm-dd>-<slug>/`, unless the user or repository instructions specify another location.

One concise report. Material findings first (bugs and merge blockers before slop), each with severity, location, observable impact, evidence, and the smallest fix. Then brief checks and
coverage limits. When the user asked for readiness or keep-or-reject, or a
concrete blocker warrants it, end with that conclusion (safe to merge vs. blocked). No required debate,
JSON, multi-agent passes, checklist report, or long empty sections.

Review-only by default. Fixes and publication follow actual authorization.
Authorization to review or fix is not authorization to stage, commit, push,
open, merge, or release. Re-run the affected checks after the last authorized edit.

## Optional deeper tools

For a large or high-risk audit, load only the extra structure the evidence
needs. These are not modes and not prerequisites of the checks above. Small checks must not run all of this machinery.

- [ai-slop.md](references/ai-slop.md) — cited-pattern quality audit
- [change-verdict.md](references/change-verdict.md) — structured keep/reject
  evidence and changed-test classification
- [rubric.md](references/rubric.md), [orchestration.md](references/orchestration.md),
  [prompts.md](references/prompts.md)
- `scripts/sweep.py`, `scripts/slice.py`, `scripts/check_findings.py`,
  `scripts/_scope.py` / `scripts._scope`
