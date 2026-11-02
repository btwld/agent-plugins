---
name: pr-comments
description: >
  Use when fetching, verifying against current `HEAD`, and skeptically triaging inline review
  threads and discussion comments from an active pull request into a prioritized action list. Do
  not use when performing a new code review from scratch (`code-review`) or drafting a pull request
  description (`pr-authoring`).
---

# PR Comments

Fetch all inline code review threads and top-level review feedback on an active pull request, verify each human or bot claim against the current `HEAD` code and tests, and group them into a prioritized action list.

## Workflow

1. Resolve the active PR for the current branch (or user-supplied PR number/URL):
   ```bash
   gh pr view --json number,url,headRefName,baseRefName
   ```
2. Fetch both inline review threads and top-level review/discussion comments (`gh pr view --comments` alone omits inline code review threads):
   ```bash
   gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate \
     --jq '.[] | {id, user: .user.login, path, line: (.line // .original_line), body, created_at, in_reply_to_id}'
   gh api repos/{owner}/{repo}/pulls/{number}/reviews --paginate \
     --jq '.[] | select(.body != "") | {user: .user.login, state, body}'
   ```
3. Verify each comment against the current codebase and tests before accepting its premise:
   - Do not blindly obey reviewer or bot comments (such as CodeRabbit, Bugbot, or Copilot).
   - Check the cited file, surrounding callers, types, and `HEAD` state to determine whether the comment identifies a real defect, is already fixed/outdated on `HEAD`, or is based on a misreading of the code.
4. Group feedback by severity and actionability:
   - **Valid & actionable** (ordered by severity: blocking bugs/regressions first, then maintainability/tests)
   - **Already fixed or outdated on `HEAD`**
   - **Disputed / incorrect** (with the concrete code or test evidence explaining why the current implementation is right)
   - **Open questions** requiring user product/design input
5. Return the concise action list. Apply code fixes only when the user has requested them, and re-run affected tests after editing.

## Output

- Grouped feedback summary (`Valid & actionable`, `Outdated/Fixed`, `Disputed with evidence`)
- Action list ordered by priority
- Open questions that still need clarification
