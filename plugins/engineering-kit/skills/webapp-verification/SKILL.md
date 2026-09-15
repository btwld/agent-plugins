---
name: webapp-verification
description: "Use when a web app or site must be verified in a real browser: reproduce UI behavior, inspect console or network evidence, check responsive or accessibility states, capture screenshots, or add and run Playwright end-to-end tests. Do not use for general web browsing, code-only review, API-only testing, browser or MCP setup, or workstation storage cleanup."
---

# Web App Verification

Prove the requested user-visible behavior in a real browser and leave reproducible evidence. This
skill owns the verification result; it does not own general web browsing, browser installation, MCP
configuration, or workstation maintenance.

## Choose the verification surface

Honor the user's explicit browser or tool choice. Otherwise choose by the evidence the task needs:

| Need | Preferred surface |
|---|---|
| Interactive exploration, visual review, screenshots, or state already open in a browser | An available host `Browser` or `Chrome` skill. Load and follow that skill before using standalone browser automation. |
| Repeatable regression coverage or CI | The repository's existing Playwright setup and bundled browser. Preserve its config, version, test location, and conventions. |
| DevTools-specific network, performance, or protocol evidence unavailable through the host browser | An already-configured Chrome DevTools MCP backend. Do not add or reconfigure one unless the user asked for setup. |
| No suitable browser capability | Report the result as blocked or unverified and provide the smallest concrete verification steps. |

A host browser's Playwright interface controls that browser session; it is not the repository's
Playwright test runner. Interactive exploration and durable tests may therefore use different
surfaces in the same task.

When authentication, persistent state, concurrent agents, shared sessions, or shutdown ownership
affect the run, read [Browser sessions](references/browser-runtime.md) before launching anything.
For requested storage diagnosis, use `dev-machine-cleanup` if available or inspect the
storage directly within the requested scope; no personal plugin is required.
Handle requested browser installation or MCP configuration with the selected tool’s setup
guidance. Routine shutdown of this task’s browser or dev server stays within verification.

## Verify the behavior

1. Inspect the repository's documented start command, existing browser tests, and target route. Use
   an existing dev server when appropriate instead of starting a duplicate.
2. Define the user flow, expected result, relevant viewport, and evidence needed to distinguish pass
   from failure.
3. Exercise the flow through the selected browser surface. Capture console, network, accessibility,
   screenshot, or DOM evidence only when it supports the result.
4. If the user requested a fix, make the smallest change supported by the observed failure and rerun
   the same flow.
5. Add or update a repository Playwright test when the user requested durable coverage or when the
   regression is valuable enough to preserve. Do not turn every exploratory check into a test.

For repository Playwright tests:

- Prefer the configured bundled browser; do not switch to installed Google Chrome unless the task
  specifically requires its behavior.
- Explore the real flow before encoding it, then use stable roles, labels, visible text, or existing
  test IDs.
- Assert user-visible outcomes rather than incidental DOM structure, generated classes, or timing.
- Run the targeted test and report the exact command and result.

## Report the evidence

State what flow, route, viewport, and browser surface were actually checked. Include relevant
screenshots, console or network findings, selectors, and test commands. Distinguish interactive
evidence from repeatable test coverage, and do not claim verification if neither ran.

Close only browser processes, tabs, profiles, and dev servers owned by this task. Report anything
left running when it matters to the user's next step.
