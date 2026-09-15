---
name: writing-plans
description: >-
  Use when requirements or an approved specification describe a multi-step software change that
  should be converted into an executable written plan before implementation. Ground the plan in
  the actual repository, order work by dependency, and scale detail to risk and executor context.
  Not for one or two obvious edits, unresolved product exploration, or executing an existing plan.
---

<!-- Derived from obra/superpowers and modified by Leo Farias for engineering-kit. See ../../SOURCES.md. -->

# Writing Implementation Plans

Turn stable requirements into the smallest plan that lets an engineer implement and verify the change without rediscovering its intent. Planning does not authorize implementation, commits, installation, deployment, or other external changes.

## Confirm a written plan is useful

Match the artifact to the work:

- For one or two obvious, reversible edits, return a short checklist instead of manufacturing a formal plan.
- For a multi-file or dependency-sensitive change, write ordered tasks with concrete validation.
- For a risky, cross-system, migratory, or multi-contributor change, include interfaces, compatibility, rollout, and recovery detail where they affect execution.

If the direction or acceptance criteria are still materially unresolved, identify the blocking decision before producing false implementation precision. Ask at most one question when the answer would change the plan's architecture or safety; otherwise state the assumption and proceed.

## Ground the plan in the repository

When the repository is available, inspect its instructions, relevant source and tests, existing conventions, and current Git state before naming work. Preserve the user's chosen design and scope unless the request explicitly authorizes reconsideration.

Capture:

- the goal and observable acceptance criteria;
- non-goals and hard constraints;
- the chosen approach and important invariants;
- affected files or components and their responsibilities;
- dependencies between changes;
- material unknowns, compatibility concerns, and rollback needs.

Use exact paths and commands only when verified. Add line numbers only when they are stable and genuinely help the executor; do not guess file locations, APIs, test names, or command output.

If repository access or required artifacts are unavailable, say so plainly. Build a discovery-first plan from facts in the request, using component responsibilities rather than invented paths. Do not fabricate repository inspection, tool calls, file contents, commit history, external skill names or refs, current configuration, or validation results. A plan that identifies what must be resolved is more executable than one built on false precision.

## Choose the output location

Honor a user-specified path first, then an established repository convention. If neither exists, return the plan in the conversation unless the user explicitly asked for a saved artifact. Do not create a new planning directory or impose source-specific path names merely because this skill was used.

## Build an executable sequence

Order tasks so prerequisites and contracts exist before their consumers. Each task should produce a coherent, reviewable outcome rather than a fixed number of tiny actions.

For each task, include what the executor needs:

```markdown
### Task: [Outcome]

**Files or components:** [verified paths and responsibilities]

**Change:** [specific behavior, interface, data, or configuration work]

**Validation:** [focused tests, analysis, build, or manual evidence]
```

Add interface signatures, schemas, commands, example payloads, migration steps, or code snippets only when they prevent a likely implementation mistake. Do not repeat complete boilerplate or require every setup, test, and edit to become its own task.

Use the repository's testing approach. Describe a test-first sequence when the user requested it or when it materially reduces implementation risk; do not impose TDD ceremony on documentation, configuration, generated-code, or trivial edits where it adds no value.

Identify sensible commit or review boundaries when they help isolate risk, but do not require a commit after every action and do not perform commits unless authorized by the implementation request.

## Cover delivery risk proportionally

Include these only when the change needs them:

- data migration, compatibility, feature-flag, or rollback steps;
- security and permission boundaries;
- observability or operational verification;
- documentation and consumer communication;
- staged rollout and post-deployment checks.

For ordinary changes, focused automated tests and the repository's standard validation commands are usually enough.

## Review the plan

Before returning it:

1. Trace every requirement and acceptance criterion to a task or state why it is out of scope.
2. Check dependency order and keep names, interfaces, and paths consistent across tasks.
3. Remove placeholders, speculative components, unrelated cleanup, and steps that do not help execution or verification.
4. Confirm the plan respects authorization boundaries and does not claim that unperformed work is complete.

End with the plan's readiness, material assumptions, and any decision the implementer still needs. Offer or begin execution only when the user's request authorizes it; do not force a particular worktree, subagent, or execution methodology.
