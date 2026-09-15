---
name: frontend-design
license: Apache-2.0; see LICENSE.txt
description: "Use when creating or redesigning an interface and visual direction, typography, layout, or interaction craft are central. Preserve an established design for scoped refinements; use design-critique for feedback only. Use visual-exploration for alternatives, image-to-code or url-to-code for faithful recreation, and design-verification for reference comparisons. Backend logic and ordinary framework fixes do not need this skill."
---

<!-- Adapted from anthropics/claude-plugins-official by Leo Farias. See ../../SOURCES.md for the source baseline and license. -->

# Frontend Design

Create a usable interface with deliberate visual choices grounded in its purpose and audience.

## Read the brief and the existing interface

Inspect the requested surface, real content, relevant components, tokens, assets, and platform conventions. Use supplied context before asking questions. If the product or intended user is unknown, ask only when that gap prevents a useful design; otherwise state a reasonable assumption and continue.

Distinguish creating a new visual direction from refining an existing interface. A scoped change preserves established identity, content, and behavior outside the request. A redesign can replace visual choices while preserving product facts and functional requirements. The user's explicit aesthetic wins over general style preferences.

## Choose a direction that serves the task

For a new direction, briefly connect palette, type, hierarchy, and composition to the subject. For an existing system, reuse its tokens and patterns. Scale the explanation to the request; a button adjustment needs no separate design document or approval stage.

- Let the primary user task determine emphasis. Operational tools prioritize scanning, predictable controls, and information density; a campaign can spend more attention on expressive imagery and type.
- Choose a coherent type scale, readable line lengths, and purposeful contrast. Use existing fonts when supplied; add a font only when it serves the brief and is available for the project.
- Use spacing, alignment, grouping, and responsive behavior to communicate relationships. Cards, gradients, borders, and decoration should serve the content rather than fill a template.
- Put expressive emphasis where it matters. A distinctive focal element works best with a disciplined supporting hierarchy.
- Use motion to explain changes and honor reduced-motion preferences. Avoid decorative movement that obstructs reading or interaction.
- Write concrete labels and realistic content. Mark demo data as illustrative; do not invent customer claims, endorsements, metrics, or capabilities.

Visual proposals do not expand the interaction contract. Include only supplied or inspected actions and states; a familiar pattern is not evidence that an action exists. Keep proposed accessibility treatments distinct from measured or tested support.

## Implement and inspect

Use the existing stack and component system. Implement requested states, responsive layouts, keyboard focus, semantic controls, and the intended interactions. Reuse suitable assets; identify any substitutions or missing resources.

Inspect the rendered result when browser or native tooling is available, covering relevant viewport sizes and interaction states. Compare against the brief and incumbent system, collect concrete defects, fix them, and recheck affected behavior. Scale verification to the change; do not invent an approval loop or a fixed polish quota. If rendering is unavailable, report that limitation rather than claiming visual verification.

Deliver the requested design or implementation, with significant decisions and remaining limitations only. A separate critique, handoff document, image-generation step, or another skill is optional when it advances the user's task.
