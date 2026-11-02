---
name: executing-plans
description: Use when implementing or resuming an existing written implementation plan with multiple tasks, dependencies, or verification steps. Follow the plan through the authorized endpoint and keep unfinished work visible. Not for writing a new plan, choosing an unresolved design, reviewing a plan without implementing it, or a simple edit that needs no plan tracking.
---

<!-- Derived from obra/superpowers and modified by Leo Farias. See ../../SOURCES.md. -->

# Executing Plans

Carry an existing implementation plan through verified completion within the user's authorized scope. Use the plan to preserve intent and track work; adapt stale details to repository evidence rather than following them blindly.

## Establish the starting point

1. Read the supplied plan and the current request. When resuming without a plan path, look in the shared project folder described by `writing-plans` for a record matching the goal and provenance; do not choose solely by modification time. Identify the intended outcome, acceptance criteria, task dependencies, and authorized endpoint. A step written in a plan is not independent permission to publish, deploy, delete data, or contact someone.
2. Inspect relevant repository instructions, source, tests, and working-tree state. Check which tasks are already complete before resuming. Preserve unrelated edits and verify completion claims against current evidence.
3. Resolve routine implementation questions through inspection. Ask only when a missing decision materially changes scope, behavior, compatibility, or authorization. Continue independent authorized work while a blocking question is pending.
4. Use the existing workspace unless isolation is needed or requested. Respect project branch rules and the user's chosen workspace. This skill does not require a worktree, a new session, or a particular task tool.

## Execute and verify

- Track pending, active, completed, and blocked work in the existing plan or available task tracker. Use a short checklist when sufficient; do not create a parallel planning system.
- Work in dependency order. For each task, inspect the affected code, make the scoped change, and run the specified checks or an appropriate equivalent supported by the repository.
- Treat test failures and missing dependencies as problems to investigate within scope, not automatic reasons to hand work back. Distinguish failures introduced by the change from existing failures. Escalate a blocker when resolving it requires unavailable access, a consequential user decision, or a change outside the authorized scope.
- Revise a stale file path, command, or implementation detail when evidence supports the correction. Explain material deviations. Revisit the plan with the user when its intended behavior or architecture must change; do not silently redesign the task.
- Mark work complete only when its acceptance criteria have supporting evidence. Distinguish implemented-but-unverified work from completed work. Do not weaken tests merely to obtain a pass.
- Share concise progress at meaningful milestones. Honor requested review checkpoints; do not invent approval pauses between routine tasks.

## Preserve continuity

Use native task tracking and context compaction when available. Keep completed work, remaining dependencies, verification results, and material decisions recoverable in the existing plan at material milestones and before a handoff. Do not force a copy-and-paste handoff or start another agent merely because the plan is long. Use delegation only when permitted and useful, respecting the user's cost preferences.

Unless the user or repository instructions specify another location, keep the saved plan in `~/.agents/projects/<project>/plans/<yyyy-mm-dd>-<slug>.md` and its linked evidence in `~/.agents/projects/<project>/evidence/<yyyy-mm-dd>-<slug>/`, using the shared project identity and provenance rules in `writing-plans`. Continue that same plan when work moves to another branch, worktree, or session; record the new worktree path, branch, commit, and session in dated progress or handoff notes rather than creating a new copy or tracker. Re-read the record before editing so concurrent work is preserved.

## Finish at the authorized endpoint

Review the result against the plan's acceptance criteria and run proportionate integration checks. Fix relevant failures and identify any remaining verification gaps. Avoid repeating an unchanged full suite without a reason.

Before staging, committing, pushing, or opening a PR, run a **pre-commit hygiene and anti-slop check** on `git status --short` and `git diff`:
- **No non-production artifacts in the repo tree:** Verify that plans, notes, reviews, and evidence stay under `~/.agents/projects/<project>/` (never committed as `PLAN.md`, `walkthrough.md`, `docs/plans/`, `.context/`, `.ws/`, debug scripts, or `.bak`/`.orig` files inside the checkout).
- **No fake or focused tests:** Confirm new and updated tests assert on real behavior and failure modes, contain no `.only` or unexplained `.skip`, and do not pass when the production change is broken.
- **No AI slop:** Strip restating comments, workaround sermons, impossible defensive checks on trusted internal paths, and unverified lint/type suppressions.

If the request already authorizes commits, a push, or a PR, complete those steps using the repository's normal workflow. Otherwise report the prepared result without extending authorization. Do not require a branch-finishing skill or reopen decisions the user has already made.

Report what was completed, meaningful deviations, verification evidence, remaining blockers, the actual delivery state, and the saved plan path. Never describe a plan as finished while required tasks remain unresolved.
