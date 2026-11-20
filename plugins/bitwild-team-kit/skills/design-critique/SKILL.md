---
name: design-critique
description: "Use when reviewing an existing screen, mockup, or user flow for usability, hierarchy, consistency, and interaction clarity. Return evidence-linked design feedback; use accessibility-review for criterion-based conformance work, frontend-design for implementation, and design-verification for fidelity against an approved target."
---

<!-- Adapted from anthropics/knowledge-work-plugins by Leo Farias. See ../../SOURCES.md for the source baseline and license. -->

# Design Critique

Explain what helps or obstructs the user's task and which design changes would matter most.

## Establish the frame

Use the supplied audience, task, design stage, and focus. Inspect the actual screenshot, prototype, design file, or live interface using available tools. A description supports conceptual feedback, not claims about unseen pixels or tested behavior. Ask for the artifact only when it is needed; review available evidence without requiring a particular connector.

## Examine the experience

Follow the intended task and consider the dimensions that affect it:

- Purpose and hierarchy: what receives attention first, whether the main action is clear, and how information is grouped and read.
- Usability: navigation, discoverability, interaction feedback, recovery, and unnecessary steps or cognitive effort.
- Consistency: terminology, spacing, type, components, and behavior against the supplied design system and platform conventions.
- States and adaptation: empty, loading, error, permission, narrow viewport, and long-content cases when visible or testable.
- Access barriers: visible risks and next checks. Do not infer keyboard behavior, screen-reader support, or measured contrast from a screenshot alone.

Match the stage: challenge the task model during exploration; give precise, scoped corrections during final refinement. Distinguish a functional obstacle from an aesthetic preference. Respect a requested visual style instead of replacing it with personal taste.

Keep recommendations usable: field labels should remain identifiable during entry, and placeholder text alone does not replace a persistent label. Propose a change as a hypothesis when its effect has not been tested.

## Return actionable findings

For each material finding, identify the location and observed evidence, explain the user consequence, and suggest a practical correction. Label an inference or untested hypothesis. Prioritize task blockers and repeated friction before cosmetic differences; avoid scores without an agreed rubric.

Include strengths worth preserving when useful. Fit the requested length and focus; do not fill every category with a finding. Critique does not itself authorize implementing changes, creating tickets, or sending feedback to others. If implementation was already requested, continue within that scope without reopening approval.
