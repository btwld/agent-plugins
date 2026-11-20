---
name: test-audit
disable-model-invocation: true
description: >
  Use when the user explicitly invokes $test-audit or asks to use the test-audit skill
  to assess or trim redundant test coverage. Trace candidate removals to the
  specific regressions the remaining suite can detect. Return recommendations
  by default and apply cuts only when the user requests edits.
---

# Test audit

Audit the selected test suite for redundant coverage. Use the revision and scope the user requested. For an audit, report recommendations. When the user requests edits, work within their file and commit constraints.

Start with the behavior callers rely on. Read the relevant contract, implementation, test assertions, and history of regressions where it explains an unusual case. For each proposed cut, name the regression the test can catch and the surviving test that would catch it through the relevant boundary. A unit test of a rule and an integration test of its wiring can both earn their place. For an obsolete requirement, cite the decision that retired it. Keep a case open when the evidence is inconclusive.

Look for repeated setup, duplicate assertions, and large matrices whose cases exercise equivalent behavior. Consolidate setup or use a table when distinct cases share a structure. Preserve distinct failure modes, including compatibility, permissions, recovery and accessibility. Use the project's requirements to decide when timing, copy, layout, or generated output is part of the contract. An audit can reasonably recommend zero removals.

For approved edits, establish a baseline and run the relevant checks after the change. When two tests appear interchangeable and the stakes justify it, introduce a small reversible fault in a disposable copy and check which tests fail. Report cuts, retained edge cases, and unresolved candidates with the supporting evidence. Give before/after counts when measured and name the checks run and any gaps.
