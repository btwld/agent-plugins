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

Honor a user-specified path first, then explicit repository instructions. Otherwise, save a plan that will be kept, executed later, or handed off under `~/.agents/projects/<project>/`. This is the user's home directory, outside every checkout and worktree; a plan returned only for discussion can stay in the conversation.

Use this shared layout, creating only the directories needed:

```text
~/.agents/projects/<project>/
  plans/<yyyy-mm-dd>-<slug>.md     # plan, progress, decisions, and handoff notes
  notes/<yyyy-mm-dd>-<slug>.md     # standalone notes for work without a plan
  reviews/<yyyy-mm-dd>-<slug>.md   # reviews the user wants kept
  evidence/<yyyy-mm-dd>-<slug>/   # supporting probes, captures, and logs
```

Resolve `<project>` from the `origin` remote's owner and repository name, joined with a hyphen and without `.git`, such as `btwld-jam`. HTTPS and SSH URLs for the same repository use the same folder. Without `origin`, use the main worktree's directory name from `git worktree list --porcelain`, not the current linked worktree's name; outside Git, use the working directory's name. Reuse an established project folder. If unrelated repositories would share a name, qualify it with the host or namespace before saving.

Before creating a record, look for one matching the work's goal and provenance. A plan belongs to a work item, which may span several worktrees; keep worktree paths in its provenance rather than adding a worktree folder to the storage layout. Continue the same record across branches, worktrees, sessions, and dates; do not select a plan solely because it is newest. Use distinct slugs for independent work, including work started on the same day. Use the same date-and-slug stem for related plans, reviews, and evidence, and link them from the plan. Keep notes for planned work in that plan; `notes/` is for work with no plan, not a second progress tracker.

Start saved Markdown records with YAML front matter containing `kind` (`plan`, `note`, or `review`), `date` (creation date in `yyyy-mm-dd` form), `repository` (owner/repository, or the main directory's absolute path without `origin`), `branch`, `commit` (full HEAD hash), `worktree` (absolute path to the checkout where the record was created), `skill`, `session` (session or transcript id), and `status` (`draft`, `approved`, or `superseded`). Record creation provenance; use YAML `null` for unavailable values rather than inventing them. Keep later worktree, branch, commit, and session changes in dated progress notes, along with completed work, remaining work, and evidence links. Read the latest contents before updating a shared record and preserve other contributors' notes.

When a client requires its own plan-mode file, follow that restriction and save a durable copy here as soon as the client permits it; identify the saved path as the record for continued work. Preserve an existing source copy when repository instructions, PRs, or other records cite it. Do not silently move or delete those sources. Include the saved path in the response or handoff so the next session can find it. Avoid `docs/` and ignored folders inside a checkout for agent records unless the user or repository instructions specify that location.

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
- staged rollout and post-deployment checks;
- for a replacement or rewrite: the chosen replacement and compatibility strategy, which legacy behavior and characterization tests must survive, and when the old code can safely be removed. Side-by-side implementation and compatibility layers are options to evaluate against actual commitments.

For ordinary changes, focused automated tests and the repository's standard validation commands are usually enough.

## Review the plan

Before returning it:

1. Trace every requirement and acceptance criterion to a task or state why it is out of scope.
2. Check dependency order and keep names, interfaces, and paths consistent across tasks.
3. Remove placeholders, speculative components, unrelated cleanup, and steps that do not help execution or verification.
4. Confirm the plan respects authorization boundaries and does not claim that unperformed work is complete.

End with the plan's readiness, material assumptions, and any decision the implementer still needs. Offer or begin execution only when the user's request authorizes it; do not force a particular worktree, subagent, or execution methodology.
