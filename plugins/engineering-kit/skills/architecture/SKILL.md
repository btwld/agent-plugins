---
name: architecture
description: >-
  Use when choosing, evaluating, or recording a consequential technical design decision from
  concrete requirements and constraints—for example a technology selection, component boundary,
  data ownership choice, or architecture decision record. Produce a recommendation sized to the
  decision and make its trade-offs and reconsideration conditions explicit. Prefer
  clean-sheet-review when the user wants an existing solution's entire framing or scope reopened;
  do not use for routine code review or an already-approved implementation task.
---

<!-- Derived from anthropics/knowledge-work-plugins and modified by Leo Farias for engineering-kit. See ../../SOURCES.md. -->

# Architecture Decisions

Turn a material technical choice into a decision that another person can understand, challenge, and revisit. Preserve the user's real constraints; do not manufacture architecture ceremony for a small or reversible choice.

## Size the decision

Choose the lightest output that makes the decision usable:

- **Compact recommendation:** a bounded, reversible choice with a small number of consequences.
- **Architecture decision record (ADR):** a consequential or long-lived choice that needs a durable record or approval.
- **Proposal evaluation:** an architecture already exists and the user wants its decision quality assessed without reopening the whole solution.

When the user requests a specific format, use it. Do not turn an evaluation into a blank ADR template or a focused decision into a full system redesign.

## Establish the decision frame

Inspect relevant repository artifacts, design notes, constraints, and observed behavior when they are available. Summarize:

- the outcome being decided;
- hard constraints and external commitments;
- the decision drivers that distinguish viable options;
- assumptions and unknowns that could change the result.

Ask at most one clarifying question when the missing answer could invert the recommendation. Otherwise proceed with an explicit assumption and say how a different answer would affect the decision.

Keep requirements separate from the current implementation. Treat latency, scale, reliability, cost, team expertise, delivery time, compatibility, security, and operational ownership as decision drivers only when the available evidence makes them relevant.

## Protect evidence and identity

Vendor capabilities and prices change. Verify exact service prices, quotas, throughput limits, retention periods, provisioning times, and migration durations from a current authoritative source inspected during the current task before quoting them. A remembered value or an uninspected documentation URL is not verification. When verification is unavailable, compare qualitatively and list the fact that must be checked; do not substitute remembered numbers. Saying an unsupported number should be verified does not make it usable—omit the number entirely unless the response can cite the source it actually inspected.

Do not include an Author, Deciders, Approvers, or contact field unless the user or a relevant artifact explicitly supplied that identity for this decision. Never use account, profile, machine, or environment identity as decision-record content.

## Compare viable options

Consider the status quo when it is genuinely viable. Compare serious options against the same decision drivers rather than listing generic pros and cons.

- Tie assessments to the stated environment and workload.
- Distinguish verified facts, reasonable estimates, and unresolved assumptions.
- Avoid invented precision. Unless the user supplied a figure or it was verified from a current authoritative source inspected during the current task, do not quote exact service prices, quotas, throughput limits, retention periods, provisioning times, or migration durations. Do not present a vendor capability as current merely because a documentation URL is known. Compare qualitatively and name the lookup or measurement needed instead.
- Do not force multiple alternatives when a hard constraint leaves only one viable choice.

Make one recommendation. Explain the primary reason, the material trade-off being accepted, and why the rejected option is not preferred under the present constraints.

## Present the result

Lead with the recommendation and a short reason. For a compact decision or evaluation, include only the sections needed to show the frame, trade-offs, consequences, missing evidence, and reconsideration conditions.

For a durable ADR, use this structure unless the repository already has a convention:

```markdown
# ADR-[number]: [Decision]

**Status:** Proposed | Accepted | Deprecated | Superseded
**Date:** [date]

## Context
[Decision, constraints, drivers, and material unknowns]

## Decision
[Chosen option and rationale]

## Options considered
[Comparable evidence and trade-offs for each viable option]

## Consequences
[What becomes easier, harder, riskier, or newly required]

## Reconsider when
[Observable thresholds or changed assumptions that should reopen the decision]
```

Add owners, approvers, implementation follow-ups, or links only when the user or repository needs them. Do not infer names, identities, email addresses, or decision authority from account or machine context; omit those fields unless the user or a relevant artifact supplied them. Do not create project-tracker tasks, modify implementation files, or imply approval unless the user requested those actions.

## Final check

Before returning the decision, verify that the recommendation follows from the stated drivers, material uncertainty is visible, consequences include the downside being accepted, and the reconsideration conditions are concrete enough to recognize later. Remove any unverified vendor number and any identity field not explicitly grounded in the request or inspected artifacts.
