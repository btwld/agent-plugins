---
name: adversarial-change-review
description: >-
  Use when the user wants a safety-biased, evidence-backed judgment of whether a specific code
  change is a genuine improvement worth keeping, merging, or porting — especially when expected
  values or tests changed, behavior preservation is disputed, or the user asks for prosecution
  versus defense. Scrutinizes the diff and changed tests, then returns KEEP, REJECT, or
  KEEP-WITH-CAVEATS. Prefer native diff review for routine PR bug-finding without a change-worthiness
  verdict, and ai-slop-review for auditing files for AI-generated slop (restating comments,
  blanket catches, hollow tests) without judging one change. Not for implementing the requested
  edits.
---

# Adversarial Change Review

Judge whether a specific code change deserves to survive. Put the burden of proof on behavior-changing code, while keeping every claim tied to evidence. A lack of proof is uncertainty—not proof that a regression exists—but unresolved uncertainty should count against risky, irreversible, or broad changes.

This is a review-only workflow. Inspect and test when useful, but do not edit or rewrite the code under review.

## Required outcome

Produce a verdict backed by four things:

- an explicit account of observable behavior before and after the change
- independent strongest-case arguments for rejection and acceptance
- a classification for every added, modified, deleted, or materially weakened test
- concrete evidence that would resolve each remaining uncertainty

Do not reward a change merely for being clever, simpler, or faster. Those qualities justify keeping it only when its behavior is correct for the intended contract and its tradeoffs are acceptable.

## Gather the evidence needed for the decision

Start from the actual review target: a git range, commit, pull request, patch, or pasted before/after code. If no target is available, ask for it; the verdict cannot be inferred from a description of the change alone.

Read the diff, then inspect only the surrounding evidence needed to verify its claims:

- the complete changed function or component and the invariants it relies on
- callers, consumers, and public interfaces that make the changed behavior observable
- tests, specifications, issue or decision context, documentation, schemas, and compatibility promises
- error and rollback paths, state transitions, concurrency boundaries, and persisted data where relevant
- history when it clarifies whether behavior is established or accidental

Run focused read-only checks or tests when they materially reduce uncertainty. Do not substitute a passing suite for behavioral reasoning: tests can preserve the wrong expectation, omit the affected path, or be weakened in the same change.

State what could not be inspected or verified. Never invent a line number; for deleted code, cite the deleted location or diff hunk as precisely as the available tooling permits.

## Reconstruct the behavior delta

Describe effects in terms a caller, user, operator, or persisted system could observe. Check the dimensions relevant to the change:

- returned values, emitted output, state changes, and side effects
- accepted and rejected inputs, null/empty/boundary handling, and equality or identity semantics
- error type, message, timing, retryability, and fallback behavior
- ordering, determinism, concurrency, cancellation, and lifecycle behavior
- public API, wire format, storage format, configuration, and compatibility
- performance characteristics when latency, memory, work amplification, or resource use crosses a meaningful contract or operational limit

Classify each material edit as:

- **Behavior-preserving:** available evidence supports the same observable contract.
- **Behavior-changing:** an observable result or operational characteristic differs.
- **Unverified:** preservation or intent depends on evidence that is unavailable or inconclusive.

Rank the delta by blast radius: external or persisted contracts first, shared internal contracts next, and local implementation details last. Keep cosmetic and mechanical changes out of the behavioral case unless they alter generated artifacts, tooling behavior, or another observable surface.

## Make two independent cases

Keep the prosecution and defense as separate passes so one does not prematurely compromise the other.

### Prosecution

Assume the change is unsafe until its behavioral claims are demonstrated. Build the strongest evidence-backed case that it should be rejected. Look especially for:

- dropped guards, widened conditions, off-by-one boundaries, and null/empty changes
- error-path, retry, timeout, transaction, or cleanup changes
- equality, identity, coercion, ordering, and default-value shifts
- compatibility breaks hidden inside a refactor or optimization
- tests that changed in the same direction as the implementation without independent support for the new contract

Do not soften this pass, but do not manufacture defects. Distinguish a demonstrated regression from a plausible risk and from missing evidence.

### Defense

Assume the change is a correct, intentional improvement and build the strongest evidence-backed case for keeping it. Look for:

- a documented contract or decision that the old behavior violated
- a concrete bug reproduced before and prevented after
- stronger invariants, narrower failure modes, or improved compatibility
- tests that add discriminating coverage instead of merely ratifying the implementation
- a measured operational benefit whose behavioral tradeoff is understood

The defense should answer the prosecution's strongest point when evidence allows. If it cannot, say so rather than inventing intent.

When the user explicitly asks for delegated or parallel reviewers, isolate these passes through the available orchestration workflow and synthesize them here. Otherwise perform two clearly separated local passes.

## Triage findings by observability and severity

Report only concrete findings or material uncertainties. For each item, give the location, the before/after behavior, who or what can observe it, and why it affects the verdict.

Separate:

- **Observable contract changes:** public behavior, persisted data, cross-module contracts, security or authorization boundaries, operational limits, and user-visible failures.
- **Internal-only changes:** implementation details with no demonstrated consumer impact.
- **Does not matter:** cosmetic or mechanical deltas with no meaningful behavioral consequence.

Order findings by expected harm and blast radius. Uncertainty is not a severity by itself; explain the concrete failure it leaves unresolved and how likely or costly that failure would be.

## Scrutinize changed tests

Inventory every added, modified, or deleted test, skipped case, changed expected value, removed assertion, loosened matcher, broader exception expectation, snapshot rewrite, widened tolerance, and reduced fixture coverage. Cross-reference each with the source or contract change that supposedly requires it.

Classify each test change:

- **(a) Intended contract update:** independent product, specification, compatibility, or decision evidence explicitly changes what the system should do; the test now encodes that revised contract.
- **(b) Legitimate tracking change:** an evidenced and intentional source change requires the expectation to move, and the revised test still discriminates correct from incorrect behavior.
- **(c) Unjustified weakening:** the change reduces regression detection, removes coverage, or moves an expectation with the implementation without enough independent support for the new behavior.

Category (c) describes the effect of the test change, not the author's motive. If the evidence cannot distinguish (b) from (c), classify it provisionally as **(c), unresolved** and name the missing spec, reproduction, or invariant that would settle it.

Call out deleted assertions and weakened expectations prominently. A source change with no corresponding test can also be a material gap, but do not pretend an unchanged test belongs in the changed-test inventory.

## Reach the verdict

Choose one recommendation:

- **KEEP:** evidence supports the intended improvement, no material observable regression remains unresolved, and changed tests faithfully protect the contract.
- **REJECT:** evidence demonstrates a regression or contract break, or the change's risk is too high for its unsupported behavioral claim.
- **KEEP-WITH-CAVEATS:** the change is probably beneficial and no demonstrated regression requires rejection, but bounded follow-up evidence, compatibility work, or monitoring is still necessary.

Do not use KEEP-WITH-CAVEATS to hide a merge blocker. If the caveat must be resolved before the change is safe, recommend REJECT until it is resolved.

State confidence as high, medium, or low and tie it to evidence quality, coverage, and unresolved scope—not rhetorical certainty. Ties and unprovable preservation lean toward caution in proportion to blast radius and reversibility.

## Report structure

Use these sections for a substantive review:

```markdown
## 1. Behavior-change summary
- Behavior-changing:
- Behavior-preserving:
- Unverified:

## 2. Triaged findings
1. [Severity] `path/to/file:line` Finding
   Observable impact: ...
   Evidence: ...

## 3. Changed-test analysis
| Test/location | Change | Class | Source/contract link | Judgment |
|---|---|---|---|---|

## 4. Prosecution vs Defense
### Prosecution
...
### Defense
...

## 5. Verdict
- Recommendation: KEEP / REJECT / KEEP-WITH-CAVEATS
- Confidence: High / Medium / Low — reason
- Risky spots: `path/to/file:line`, ...
- Evidence that would resolve doubt: exact test, specification, value, or invariant to confirm
```

Keep empty categories brief. If no tests changed, say so in section 3. Cite concrete `file:line` locations throughout, and label inferences and unavailable evidence explicitly.
