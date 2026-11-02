---
name: pr-prep
description: >
  Use when preparing a pull request or branch for easier review by cleaning or reorganizing noisy
  commit history into logical dependency-ordered commits (while proving git tree identity) and
  adding reviewer entry-point guidance without changing code behavior. Do not use for general code
  review (`code-review`) or feature implementation.
---

# Make PR Easy to Review

Prepare a PR so a reviewer can quickly understand the intent, important files, and risk. The default goal is reviewability without behavior changes.

## Workflow

1. Resolve the target PR from the user-provided URL or current branch.
2. Inspect commits, diff size, changed paths, generated files, and PR description.
3. Run the **Pre-PR Hygiene & Anti-Slop Gate** before reorganizing commits:
   - **Evict non-production artifacts (`S16`):** Check `git diff <base>...HEAD --name-status` and `git status` for stray agent plans, walkthroughs, notes (`PLAN.md`, `IMPLEMENTATION_PLAN.md`, `walkthrough.md`, `docs/plans/`, or Markdown files with `kind: plan|note|review` frontmatter), `.context/` or `.ws/` directories, one-off debug scripts (`debug_*`, `scratch_*`, `tmp_*`), and backup files (`*.bak`, `*.orig`). Move durable agent records to `~/.agents/projects/<project>/` and remove stray files from the branch before locking the tree hash.
   - **Reject fake or focused tests (`S10`):** Check touched test files for `.only` / unexplained `.skip`, tautological assertions (`expect(x).toBe(x)`, `toBeDefined()`-only), mock-only assertions that never verify behavior, or weakened assertions.
   - **Strip AI and structural slop (`S1–S15`):** Remove restating comments, workaround sermons, impossible defensive checks, stale lint suppressions, and unjustified >1,000-line file sprawl.
4. Identify reviewability issues: noisy commits, stale description, unrelated changes, mixed mechanical and logic changes, missing tests, or unclear reviewer entry points.
5. Propose a plan before rewriting history or force-pushing.
6. Apply safe improvements, then verify the cleaned tree matches across commit reorganization.

## History Cleanup

Only rewrite history when the user asks for it or agrees to the plan. Before rewriting:

```bash
gh pr view <PR> --json title,headRefName,baseRefName,state,commits
git fetch origin <headRefName> <baseRefName>
ORIGINAL_TREE=$(git rev-parse origin/<headRefName>^{tree})
```

Good commit groupings usually follow dependency order:

1. Schema/storage or generated API definitions.
2. Core logic.
3. Wiring and integration.
4. UI or surface behavior.
5. Tests.

After rewriting, verify content identity:

```bash
echo "Original tree: $ORIGINAL_TREE"
echo "Current tree:  $(git rev-parse HEAD^{tree})"
git diff origin/<headRefName> --stat
```

Do not push if the tree changed unintentionally.

## Reviewer Guidance

When code behavior should stay untouched, prefer PR description and review notes:

- Add a TL;DR that matches the actual diff.
- Separate core files from generated or mechanical files.
- Call out risky behavior changes, migration order, rollout plan, and test coverage.
- Link issue trackers, dashboards, or design docs when they explain intent.

## Guardrails

- Never hide meaningful behavior changes inside "cleanup".
- Do not bypass hooks unless the user explicitly asks.
- If the PR is too large to make reviewable with notes, recommend splitting instead of polishing around the problem.
