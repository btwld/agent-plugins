---
name: url-to-code
description: "Use when the user asks to faithfully recreate a live website or specified web flow as a local frontend prototype using browser inspection. Not for a redesign inspired by a URL, screenshot-only implementation, general browsing, or backend/service cloning."
---

# URL to Code

Recreate the requested visible web experience from inspected source evidence.

## Inspect the source

Identify the exact URL, pages or flow, destination, and requested fidelity. A request for a design inspired by a site is not a faithful clone; use its stated design goal instead. Use the user's chosen browser or an available host browser following its documented interface.

Open the source and verify that the expected page is visible. A login wall, error page, redirect, or inaccessible source is not evidence of the requested experience. Explain what is accessible and what cannot be recreated faithfully; do not substitute guesses for capture. Ask the user to sign in through their browser or supply screenshots; never ask them to paste passwords, access credentials, or session tokens into chat.

Inspect the requested pages at relevant viewport sizes. Capture significant sections and states, including off-screen or lazy-loaded content when in scope. Collect visible text, layout, fonts, colors, and reusable asset references from actual page evidence. Inspect DOM or computed styles when available rather than guessing exact values.

Exercise reversible controls needed to understand the requested flow. Do not submit purchases, send messages, change accounts, or perform other external actions merely to discover behavior. Mark untested transitions and use supplied evidence where available.

## Build the local experience

Use the destination project's framework and components. In an empty project with no prescribed stack, use static HTML/CSS/JavaScript for a small prototype. Keep source capture and local recreation distinct.

Build only the agreed pages and core interactions. Default to frontend-only behavior; mark sample data and local state clearly. Do not clone authentication, integrations, persistence, or backend services unless explicitly requested. Never capture credentials or bake session tokens into output.

Reuse assets when their use is permitted; access to an asset alone does not establish permission. Use supplied or appropriately licensed alternatives when needed and document substitutions. Keep necessary local assets in the project rather than depending on private or ephemeral source URLs.

## Verify the recreation

Run the local app, compare captured source and local implementation at the same viewport and state, and test the scoped flow locally. Use the separate design-verification skill for a dedicated fidelity review when useful; general browser behavior testing belongs to webapp-verification.

Correct observed material differences within scope and recapture after fixes. Do not claim successful fidelity without inspecting both artifacts. If source or local rendering is blocked, identify which part is implemented and which remains unverified. Avoid repeated retries without a new approach.

Deliver the local preview or artifacts, the captured scope, working interactions, substitutions, and known gaps. Deployment and publication are separate actions and require existing authorization.
