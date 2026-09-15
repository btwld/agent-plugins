---
name: ux-copy
description: "Use when writing or reviewing interface labels, errors, confirmations, onboarding, empty states, or other UX microcopy where wording must match product behavior and constraints. General marketing copy and document editing are separate tasks."
---

<!-- Adapted from anthropics/knowledge-work-plugins by Leo Farias. See ../../SOURCES.md for the source baseline and license. -->

# UX Copy

Write interface text that helps the user understand a state and take the right action.

## Ground the wording

Use the actual screen, audience, established terminology, product behavior, and length constraints. Read supplied context before asking for more. Match the brand voice while giving errors and consequential actions appropriate clarity.

Do not invent the reason an operation failed, recovery options, data retention, timing, or reversibility. When behavior is unknown, keep copy truthful and identify the decision needed. Preserve established factual copy outside the requested scope.

## Choose the relevant pattern

- Actions: name the result with a clear verb. Keep the same action name across the button, progress state, and completion message.
- Errors: explain what is known, the consequence, and a real next step. Avoid blame, unsupported causes, and generic reassurance.
- Empty states: distinguish no data, no matches, insufficient permission, and failure to load. Offer an action only when it is available.
- Confirmations: name the object and consequence. State permanence only when established. Preserve material object counts and distinguish local removal from deletion of originals. Button labels should distinguish the choices clearly.
- Loading and progress: describe the actual process without fabricated estimates or guarantees.
- Onboarding and help: reveal information at the moment it becomes useful. Do not hide essential instructions in a tooltip alone.

Prefer plain terms, concrete outcomes, and concise sentences. Account for localization, text expansion, pluralization, and accessible names where relevant. Respect explicit character limits, counting the actual output rather than estimating.

## Deliver

Return the requested copy first. Give alternatives, rationale, or localization notes only when requested or needed to resolve a meaningful tradeoff. A request for one label can receive one label. Check wording against observed behavior, terminology, and constraints before returning it.
