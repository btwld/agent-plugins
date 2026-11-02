---
name: ci-loop
description: >
  Use when watching pull request CI checks, diagnosing failing PR jobs, and iterating on minimal
  targeted fixes until all required PR checks are green using `gh pr checks` as the source of
  truth. Do not use for authoring a new pull request description (`pr-authoring`) or performing a
  static code review without CI checks (`wild-code-review`).
---

# CI Loop

Watch the active pull request's CI checks, pull logs for failing jobs, apply the smallest safe fix for each root failure, and repeat until all required PR checks pass.

Use `gh pr checks` as the source of truth because it covers every check attached to the PR, whereas `gh run list` only covers GitHub Actions workflows.

## Workflow

1. Resolve the PR for the current branch (`gh pr view --json number,url,headRefName`).
2. Inspect current PR checks (`gh pr checks --json name,bucket,state,workflow,link`) before waiting.
3. If checks already failed, inspect failed jobs and extract the first actionable root error. Use `gh run view <run-id> --log-failed` when the check links to a GitHub Actions run; otherwise use the external check link to identify the failing command or service.
4. If checks are pending, watch with `gh pr checks --watch --fail-fast`.
5. Apply the smallest safe fix for one actionable failure at a time; when push is authorized, push and re-check the full PR check set until green.

## Commands

```bash
# Resolve the active PR
gh pr view --json number,url,headRefName

# Inspect all attached checks
gh pr checks --json name,bucket,state,workflow,link

# Watch pending checks and fail fast
gh pr checks --watch --fail-fast

# GitHub Actions logs, when the failing check links to a GHA run
gh run view <run-id> --log-failed
```

## Guardrails

- Keep each fix scoped to a single failure cause when possible.
- Prefer minimal, low-risk changes before broader refactors.
- Do not bypass hooks (`--no-verify`) to force progress.
- If the failure is clearly unrelated to the PR and appears fixed on `main`, merge or rebase onto latest `main` instead of bloating the PR with unrelated fixes.
- If failures are flaky, retry once and report flake evidence.
- Re-run `gh pr checks --json name,bucket,state,workflow,link` after every push; the check set can change.

## Output

- Primary failing job and current CI status
- Failure summary and fixes applied in iteration order
- PR URL once checks are green
