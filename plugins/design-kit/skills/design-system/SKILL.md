---
name: design-system
description: "Use when auditing, documenting, or extending an existing design system of tokens, component variants, states, and patterns. Ground recommendations in actual design or code sources; general visual redesign and isolated styling fixes are separate tasks."
---

<!-- Adapted from anthropics/knowledge-work-plugins by Leo Farias. See ../../SOURCES.md for the source baseline and license. -->

# Design System

Make shared interface decisions consistent, reusable, and explicit without introducing a second source of truth.

## Choose the task and source

Identify whether the request is an audit, component documentation, or a system extension. Inspect the relevant implementation, design library, theme, tokens, and documentation. State which source governs the decision; flag disagreements instead of silently treating a design file or code repository as universally authoritative.

Keep the review bounded to the requested system or component. Use available files and tools; Figma or a wiki is optional unless the task specifically requires accessing it.

## Audit

Trace actual token use, semantic naming, component variants, supported states, responsive behavior, and documented interfaces. Show representative locations and user or maintenance consequences. A literal value is not automatically a defect: check whether it represents an intentional exception, an underlying token definition, or a repeated semantic decision that should be shared.

Equal values do not establish a shared dependency: a literal matching a token today will not track later token changes. Flag that maintenance implication when the contract calls for the token; do not treat an intentional literal exception as a defect. Partial excerpts also do not prove a prop is undocumented or unsupported outside the inspected scope.

Distinguish measured counts from sampled observations. Avoid completeness scores without a defined rubric. Prioritize inconsistent behavior, inaccessible patterns, broken contracts, and repeated divergence over cosmetic renaming.

## Document or extend

For documentation, describe the actual purpose, usage boundaries, variants, properties, defaults, states, interactions, and relevant accessibility behavior. Mark unknown or unverified facts. Do not invent APIs, token names, or interaction support to fill a template.

For an extension, explain the unmet need and inspect existing patterns before proposing another abstraction. Define only necessary variants and states. Separate confirmed constraints from proposed choices; show how the proposal composes with the existing system.

If edits are requested, account for consumers, compatibility, and migration effort. Prefer a scoped implementation or documented exception when a new token layer or component abstraction would add more cost than reuse.

## Deliver and verify

Return the requested findings, component documentation, proposal, or implemented change. Point to inspected sources and state remaining unknowns. For changes, run relevant component checks and inspect affected visual/interaction states where possible. Do not publish documentation, replace a library, or create a migration project merely because an audit found opportunities.
