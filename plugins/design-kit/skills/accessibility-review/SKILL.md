---
name: accessibility-review
description: "Use when checking an interface against accessibility criteria with explicit scope and evidence. Use relevant browser, native, or design tools to inspect behavior; a screenshot-only review cannot establish full conformance."
---

<!-- Adapted from anthropics/knowledge-work-plugins by Leo Farias. See ../../SOURCES.md for the exact upstream baseline and license. -->

# Accessibility Review

Identify access barriers and distinguish verified failures from untested requirements.

## Establish scope

Use the requested standard, version, level, platform, and user flow. If no target is specified, propose WCAG 2.2 AA for a web review and identify that assumption. Check the authoritative criterion and exceptions before making an unfamiliar or consequential pass/fail claim.

Inspect the actual artifact with available appropriate tools. Separate design intentions, DOM or accessibility-tree observations, automated findings, keyboard tests, and assistive-technology results. An unavailable test is not a pass.

## Examine relevant barriers

- Perception: meaningful text alternatives, structure, text contrast, non-text contrast, and information conveyed without color alone.
- Operation: keyboard access, focus order and visibility, unobscured focus, modal behavior, alternatives to dragging, and pointer target size.
- Understanding: labels, instructions, error identification and recovery, predictable interaction, and accessible authentication where applicable.
- Robustness: programmatic names, roles, states, values, and relevant status announcements.
- Adaptation: text resizing, reflow, zoom, and motion preferences where relevant to the chosen criteria.

Measure text contrast from actual colors and relevant typography. Under SC 1.4.3, normal text generally requires 4.5:1 and large text 3:1; verify applicability and exceptions. A visual impression cannot establish those ratios.

Distinguish target-size criteria: WCAG 2.2 SC 2.5.8 is AA and generally requires 24 by 24 CSS pixels or a qualifying exception. SC 2.5.5 is AAA and generally requires 44 by 44 CSS pixels with its own exceptions. Do not report the AAA threshold as a blanket AA failure.

## Deliver

For each finding, give the affected element, reproduction or measurement, criterion and level, user impact, and a practical fix. Mark missing evidence as a next check. Prioritize barriers by affected tasks, rather than inventing a score or a percentage of issues caught by automation. Claim conformance only when the completed evaluation scope supports it.

## Criterion references

Checked 2026-09-10. Consult these for exact definitions and exceptions when applicable:

- [Text contrast, SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [Minimum target size, SC 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
- [Enhanced target size, SC 2.5.5](https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html)
