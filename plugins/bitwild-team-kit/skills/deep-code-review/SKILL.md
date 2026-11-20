---
name: deep-code-review
description: >
  Use when reviewing or auditing a pull request, commit, diff, staged snapshot,
  working tree, pasted patch, files, or repository for defects, regressions,
  missing tests, suspicious or unnecessary code, hollow tests, stray
  non-production or planning artifacts, AI-generated code slop, structural
  maintainability, language/framework idioms, API/documentation consistency,
  stacked PRs, or adversarial keep/reject change verdicts. Do not use to
  implement features, author a pull request, redesign a system, or declare a
  canonical implementation.
---

# Deep Code Review

One review. Every pass considers correctness, suspicious or unnecessary code,
and hollow or tautological tests, then skeptically challenges both the change
and each suspected finding. Depth scales with scope and risk. A user-narrowed
scope still governs. Do not start this skill after every implementation;
ordinary review language is enough.

Neighboring owners stay separate: do not implement features, author
a PR ([pr-authoring](../pr-authoring/SKILL.md)), redesign
whether something should exist ([clean-sheet-review](../clean-sheet-review/SKILL.md)),
or audit a canonical example ([reference-implementation](../reference-implementation/SKILL.md)).
The simplification pass recommends changes. Use [code-simplifier](../code-simplifier/SKILL.md) for explicitly requested refinement. Suite-wide redundancy analysis belongs to the separately invoked [test-audit](../test-audit/SKILL.md) skill.

## Review

1. Pin the target and constraints. Name the exact snapshot: commit, range, PR,
   staged index, working tree, or pasted snippet. Do not mix dirty-tree files
   into a commit or staged review. For a stacked PR, establish its immediate
   parent and immutable base/head commits; verify that the comparison captures
   the intended increment after rebases, squashes, or retargeting. Attribute
   inherited issues separately from new interactions. For a whole-stack review,
   check each increment and the cumulative result without duplicating findings.

2. Establish the package's purpose from requirements, the PR description,
   documented contracts, and real consumers. Trace affected behavior through
   callers. Separate binding constraints from historical design choices and
   assumptions. Read nearby project patterns and identify the obligation each serves.
   If a familiar pattern conflicts with a caller’s contract, trace the conflict to
   its observable effect and explain whether this change introduces or exposes it.
   Identify supported language/runtime and dependency versions.
   Work inline for ordinary reviews; use the comprehensive review guidance
   below when the user requests deeper or delegated review.

3. Check in priority order:
   - **Bugs, regressions, and contracts (highest priority):** observable
     behavior, error handling, ordering/concurrency, security boundaries, and
     swallowed failures.
   - **Test authenticity and repo hygiene:** changed or removed assertions;
     hollow or tautological tests, mock-only assertions, or `.only`/`.skip`
     leaks; and stray non-production files, agent plans, walkthroughs, or debug
     artifacts without a maintained repository purpose. Check actual consumers,
     build/package rules, fixture discovery, and repository policy before calling
     a file unused. A test that moves with the implementation needs independent contract support.
   - **Idioms and ecosystem practices:** language-appropriate constructs, real
     supported APIs, resource ownership, and framework lifecycle rules. Verify
     material claims against official version-appropriate documentation or
     installed source; local skills are guidance, not proof. Explain the
     concrete benefit or contract violation, not just “best practice.”
   - **API and documentation consistency:** compare changed behavior, defaults,
     errors, types, configuration, and public symbols with callers, examples,
     README/API docs, required migration notes, and PR promises. Now-stale
     documentation is in scope even when untouched. Check generated-doc sources
     and workflows rather than requesting manual output edits.

4. For each suspected defect, give the smallest realistic input or sequence that
   produces the wrong result. Try to disprove each suspected finding against
   docs, types, callers, and other counterevidence. Distinguish defects, risk, and missing evidence.
   For concurrency or race risks that a single test run may not trigger,
   disprove by showing the interleaving is impossible or already synchronized.
   Clean code can produce no findings. Skeptical does not mean reflexively
   rejecting. A smell needs a concrete behavioral or maintenance cost and a
   feasible correction. Type annotations alone do not prove a guard unnecessary
   at a runtime boundary; a mock or fixture is not inherently a fake test.

5. Run only focused, safe checks against the named baseline. Inspect unfamiliar code and build scripts before executing them. Isolate execution.
   Do not invent runs. A pre-existing failing test is not evidence that this
   change is wrong unless you show the change caused it. Identify a plausible
   regression that important changed tests should reject. Use a focused
   reproduction or mutation in a disposable copy when it resolves doubt.

6. Make a separate simplification pass over the reviewed change. Trace the
   behavior a caller relies on. Could a single owner, a simpler state model, or
   removing a forwarding layer preserve the same outputs, errors and ordering?
   Identify the responsibility each proposed removal currently serves. Report a
   reachable invalid state as a defect with its triggering sequence. Report a
   behavior-preserving improvement as optional cleanup with a concrete benefit.
   Do not infer AI authorship.

## Comprehensive or delegated reviews

For a final pre-merge review, use [reviewer-lenses.md](references/reviewer-lenses.md)
to examine the material risks and run the simplification pass. One reviewer can
do both. When delegation is requested, assign independent questions according to
the change, then have the lead verify findings and give one merge verdict.

Give independent reviewers the same pinned scope, requirements, versions, and
relevant lens/evidence brief, without another reviewer's suspected findings.
Use fresh minimal contexts where supported. Fit work to available concurrency;
queue remaining lenses or cover them inline, with no recursive reviewer teams.
Honor explicit user constraints; if delegation is prohibited or unavailable,
perform the passes inline and disclose the limit. Wait for assigned results,
re-read material evidence, resolve disagreements, and deduplicate. Agreement is
not proof; an unfinished reviewer is not a clean result.

## Report

When the user asks to keep a review, save it at `~/.agents/projects/<project>/reviews/<yyyy-mm-dd>-<slug>.md` using the shared project identity and provenance fields from `writing-plans` with `kind: review`, and link supporting files under the matching `~/.agents/projects/<project>/evidence/<yyyy-mm-dd>-<slug>/`, unless the user or repository instructions specify another location.

One concise report. Material findings first (bugs and merge blockers before slop), each with severity, location, observable impact, evidence, and the smallest fix. Then brief checks and
coverage limits, including the reviewed snapshot and unreviewed areas. Keep
actionable cleanup separate from defects without inflating severity. For a final review, a readiness request, or a concrete blocker, give one verdict
from these outcomes: changes required, no blocking findings in the reviewed
scope, or review incomplete.
State material uncertainty; never imply guaranteed correctness. No required
debate, JSON, checklist report, or long empty sections.

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
