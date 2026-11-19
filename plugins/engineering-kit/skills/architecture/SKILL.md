---
name: architecture
description: >-
  Use when choosing, evaluating, or remembering a technical design decision: technology
  selection, component boundaries, data ownership, or a chosen API contract. Give a concise
  recommendation and its reason, main trade-off, and conditions for reconsideration. Use
  clean-sheet-review to reopen an existing solution's whole framing, wild-code-review for
  code defects, and ordinary execution for an approved implementation.
---

<!-- Derived from anthropics/knowledge-work-plugins and modified by Leo Farias. See ../../SOURCES.md. -->

# Architecture

Make the technical choice clear and easy to remember. Keep the decision proportional to
its consequences; a long-lived choice does not require a long document or a formal ADR.

## Understand the decision

Inspect relevant requirements, repository evidence, existing decisions, and real consumers.
Identify the outcome, fixed constraints, and unknowns that could change the recommendation.
Preserve the user's chosen scope. Ask only when a missing fact would materially change the
choice; otherwise state a reasonable assumption.

Distinguish choosing a direction from developing one already chosen. For consumer examples,
errors, compatibility, and testable API requirements, read
[api-contract-design.md](references/api-contract-design.md). Do not reopen settled choices
or turn a focused evaluation into a system redesign.

## Recommend the smallest suitable solution

Compare viable options against the actual constraints, including the existing approach when
it remains suitable. Do not invent alternatives, components, or requirements to fill a template.
Explain the strongest reason for the recommendation and the material cost or limitation accepted.
Separate observed facts, proposals, and unresolved questions; recommending a choice does not
mean it has been approved.

Verify changing vendor capabilities and exact prices, quotas, throughput ceilings, retention
periods, or migration estimates against current authoritative evidence before citing them.
An uninspected URL or remembered number is not verification. If evidence is unavailable,
compare qualitatively and name the fact or measurement needed.

## Remember the choice concisely

Lead with the decision or recommendation. Usually a short paragraph or these four lines is enough:

- **Decision:** what we chose, or what is proposed if it is not settled.
- **Why:** the requirement or constraint that drove it.
- **Trade-off:** the main limitation we accept.
- **Revisit:** what concrete change would warrant another look, if relevant.

Use only the detail needed to understand and act on the choice. Add consumer examples or
compatibility details when requested or necessary; concision must not hide an unresolved contract.
Do not add invented owners, approvers, dates, scores, or exhaustive option matrices.

When the decision needs to persist, update the relevant existing plan or project documentation
using its established location. Keep one authoritative explanation and link to it rather than
copying it into another tracker. A discussion-only recommendation can stay in the conversation.
If no suitable record exists and the user asks to save the decision, create a short project note
in the requested or established location. Distinguish a proposed change from an accepted decision,
and preserve relevant history when a choice changes.

Use the project's formal ADR format when the user asks for it or the repository requires it. Do not generate numbered ADR files, an ADR
folder, or a separate approval workflow by default. Respect existing records and repository
requirements; do not delete or silently replace them to simplify the format.

Before finishing, check that the recommendation follows from the evidence, the main trade-off
is visible, and any saved note can be found. Report material uncertainty plainly. Do not create
tickets, modify implementation, commit, or publish beyond the user's authorized scope.
