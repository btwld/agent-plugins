---
name: image-to-code
description: "Use when faithfully implementing a selected screenshot, mockup, or reference image as a responsive interface. Not for choosing a new visual direction, cloning a live URL, general UI fixes, or direct Figma operations owned by the Figma plugin."
---

# Image to Code

Implement the selected visual target with traceable decisions about fidelity and behavior.

## Establish the target

Open the actual reference image. Confirm the requested screen or component, destination project, and implementation scope from existing context. Use the existing stack, design tokens, components, and assets. For an empty project, use the user's requested framework; otherwise a small static HTML/CSS/JavaScript prototype is sufficient unless the task needs more.

Record the target's dimensions, content, layout regions, typography, and assets. Distinguish measured properties from estimates. A screenshot shows a state, not how every control works. Use supplied behavior requirements; identify inferences and keep them minimal. Do not expand scope into authentication, persistence, APIs, extra routes, or deployment unless requested.

If the image cannot be inspected, name the missing evidence. Do not infer its appearance from its filename. A Figma source that requires Figma access belongs to that tool's workflow; a supplied exported image can be used directly.

## Build from evidence

Implement layout, hierarchy, text wrapping, spacing, colors, and asset placement in the target state. Reuse supplied assets and suitable icon libraries; source or generate additional imagery only when needed and available. Document substitutions instead of claiming an approximate logo or font is exact.

Use semantic controls and visible focus. Make the requested core interactions work, using clearly identified local demo behavior where appropriate. Keep nonfunctional controls distinguishable; do not claim a backend exists. Avoid implementing the entire screenshot as a single raster image.

Support the supplied viewport and reasonable resizing without inventing a different design. Where only one viewport is supplied, describe responsive adaptation as our implementation choice rather than source evidence.

## Inspect and hand off

Run the implementation using the project's established command and available browser or native preview tools. Inspect the rendered target state and requested interactions. For visual fidelity, compare the reference and implementation at matching viewport, crop, and state; the standalone design-verification skill can perform that comparison when useful.

Fix material discrepancies within the authorized scope and recheck changed regions. Stop repeated ineffective attempts and report the unresolved cause rather than polishing indefinitely. If rendering is unavailable, deliver the implemented artifact with that explicit verification gap.

Return the files or preview, actual checks, significant deviations, and remaining limitations. Local implementation does not authorize publication. Preserve unrelated project changes.
