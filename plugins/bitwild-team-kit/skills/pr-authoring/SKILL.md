---
name: pr-authoring
description: "Use when preparing a branch for review, drafting or revising a PR title and description, or creating/updating the PR when requested. Includes optional commit-history cleanup. Standalone commits/pushes, issue searches, code review, CI repair, and comment triage are separate tasks."
---

# PR Authoring

Make the change easy to review through its scope, description, and commit structure. Use only the operations the request needs; preparation is not a mandatory stage before writing a description.

<!-- Includes adapted PR preparation guidance from cursor/plugins. See ../../SOURCES.md and ../../licenses/cursor-team-kit-MIT.txt. -->

## Ground the work

Identify the repository, base/head, existing PR if any, and requested outcome: local preparation, a text draft, or a GitHub update. Inspect the complete base-to-head diff, relevant commits, repository template, and actual validation. A local branch need not be pushed for preparation or drafting. Preserve unrelated work. Flag stray local artifacts and unintended focused or disabled tests found in the diff; verify their purpose before calling them defects.

For preparation, distinguish core changes from mechanical files and identify confusing commit boundaries or stray local artifacts. Verify an artifact's purpose before proposing removal. Recommend splitting unrelated changes when reviewer notes cannot make the scope coherent. For history changes, read [history-cleanup.md](references/history-cleanup.md); a vague request to tidy a PR does not authorize rewriting or force-pushing.

## Write for the reviewer

Use a title that names the resulting behavior. Lead the body with the concrete problem and resulting behavior. Follow the repository template, adding only material validation, compatibility, migration, and reviewer-entry-point information. Avoid file-by-file narration, empty sections, invented checks, and agent/provider authorship boilerplate. Product or API names remain appropriate when they explain the change.

Use only explicitly supplied or inspected issue references; do not search for a possibly related issue. Closing keywords apply only to a fully resolved issue targeting the default branch; otherwise use a related link. Omit linkage when no issue is known. Put assumptions or questions for the user outside the reviewer-facing body.

For visible or interactive changes that need evidence, read [visual-evidence.md](references/visual-evidence.md). Keep unverified claims and missing artifacts explicit.

## Deliver at the requested endpoint

A draft request returns the title and body, with the body inside one fenced Markdown block. It makes no GitHub write. Creating/updating a PR requires that action to be authorized; read [publishing.md](references/publishing.md) when it is. Commit, push, history rewrite, and publication follow their own authorized scope.

Report the draft, preparation result, or PR link with actual validation and remaining gaps. CI repair, reviewer-comment triage, and defect review remain separate tasks; do not start them automatically.
