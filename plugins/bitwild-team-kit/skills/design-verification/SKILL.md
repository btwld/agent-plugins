---
name: design-verification
description: "Use when comparing a rendered implementation against an approved screenshot, mockup, or captured design reference to verify visual fidelity. Requires both artifacts. Not for general design critique, functional browser testing, accessibility certification, or creating a new design."
---

# Design Verification

Determine whether the implementation matches its approved visual target. Review the actual artifacts and make discrepancies actionable.

## Establish comparable evidence

Identify the approved reference, rendered implementation, requested screen, and relevant state. Open or capture both artifacts with available tools. Code inspection and descriptions alone cannot establish visual fidelity.

Match viewport, content, theme, route, interaction state, crop, and image density. Compare the application region rather than unrelated browser chrome or a decorative device frame. Record material normalization and estimates. A density or crop mismatch should be resolved before it becomes a design finding.

If a required artifact or state is unavailable, report which comparison is unverified. Continue independent checks that have sufficient evidence without inventing a pass for the missing portion.

## Compare the design

Inspect both images together when the tools allow it. Compare the overall composition, then focus on regions where small differences affect meaning or fidelity. Review:

- Typography: font family or fallback, weights, scale, line height, wrapping, and truncation.
- Layout: alignment, region proportions, spacing rhythm, density, clipping, and responsive behavior supported by the reference.
- Colors: token consistency, semantic states, and visible foreground/background differences.
- Assets: correct subject, crop, resolution, shape, and approved substitutions.
- Copy: labels, values, ordering, and content that changes layout or user understanding.

Distinguish an objective mismatch from an aesthetic preference, intentional deviation, or missing design specification. A screenshot does not prove keyboard behavior, screen-reader support, or complete accessibility conformance. Do not redesign the approved target as part of fidelity review. A wrong button label establishes a copy mismatch; it does not establish which action the handler performs. Keep potential user confusion separate from unverified destructive behavior.

## Report and optionally recheck

For each material finding give location, reference-versus-implementation evidence, user or fidelity impact, and a concrete correction. Prioritize unusable or missing content, then substantial differences, then minor refinements. Avoid numeric precision unsupported by measurements.

This skill is review-only unless the user also authorized fixes. After an authorized correction, capture the affected implementation state again and verify it against the reference. Do not mark an issue resolved solely because code changed. Stop repeated ineffective attempts and explain what remains; no automatic continuation hook or mandatory polish quota is needed.

Return a concise verdict: matches the inspected scope, has material differences, or cannot yet be verified. Include artifact paths or links, the compared viewport/state, accepted deviations, and unresolved gaps. A pass applies only to the inspected visual scope and is not a functional test result. Create a separate report file only when requested or useful for a substantial review.
