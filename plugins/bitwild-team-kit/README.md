# Bitwild Team Kit

Choose the skill for the outcome you need. All skills below use the same install and Claude command prefix. [Installation and migration](../../README.md#install)

## Engineering and writing

| What you want to finish | Where to start |
| --- | --- |
| Write something people need to understand or act on | [Writing for Humans](skills/writing-for-humans/SKILL.md) for READMEs, procedures, issue descriptions, and technical explanations. |
| Write instructions an agent can carry out | [Writing for Agents](skills/writing-for-agents/SKILL.md) for skills, repository instructions, and agent reference material. For a mixed documentation request, match each artifact to its reader. |
| Decide whether a change is ready to merge | [Deep Code Review](skills/deep-code-review/SKILL.md). Trace correctness against callers and requirements, challenge suspected findings, then make a separate simplification pass. The result is one review and one readiness verdict. |
| Decide how to build something | [Architecture](skills/architecture/SKILL.md) for a technical decision, [Writing Plans](skills/writing-plans/SKILL.md) for implementation steps, or [Executing Plans](skills/executing-plans/SKILL.md) to carry out an existing plan. |
| Prepare and land a pull request | [PR Authoring](skills/pr-authoring/SKILL.md) prepares the branch or drafts the PR. Use [PR Comments](skills/pr-comments/SKILL.md) for existing feedback and [CI Loop](skills/ci-loop/SKILL.md) for failing checks. |

### Focused requests

- [Test Audit](skills/test-audit/SKILL.md) is explicitly callable for suite-wide redundancy. Every proposed cut needs a surviving test that catches the same regression. [Code Simplifier](skills/code-simplifier/SKILL.md) applies explicitly requested behavior-preserving cleanup.
- [Verify](skills/verify/SKILL.md) measures a specific behavior claim. [Clean-Sheet Review](skills/clean-sheet-review/SKILL.md) reopens the design decision. [Reference Implementation](skills/reference-implementation/SKILL.md) reviews a canonical example others will copy.
- [PR Canvas](skills/pr-canvas/SKILL.md) creates a requested interactive walkthrough. [SBVR](skills/sbvr/SKILL.md) formalizes shared business vocabulary and rules.

Existing commands still work. [wild-code-review](skills/wild-code-review/SKILL.md) runs Deep Code Review, and [pr-prep](skills/pr-prep/SKILL.md) runs the preparation step of PR Authoring. Both compatibility names require explicit invocation.

## Product and delivery

| Skill | Outcome |
| --- | --- |
| [product-brainstorming](skills/product-brainstorming/SKILL.md) | Explore problems, alternatives, assumptions, and product opportunities |
| [research-synthesis](skills/research-synthesis/SKILL.md) | Turn supplied research and customer feedback into traceable findings |
| [competitive-brief](skills/competitive-brief/SKILL.md) | Compare alternatives for positioning and build-versus-buy decisions |
| [ux-friction-research](skills/ux-friction-research/SKILL.md) | Investigate public user difficulties or review an existing friction log |
| [write-prd](skills/write-prd/SKILL.md) | Product, module, and feature PRDs with structured requirements, questions, and decisions |
| [write-wbs](skills/write-wbs/SKILL.md) | Work packages, primary/contributing coverage, stages, releases, dependencies, and WBS reviews |

For a short spec or work breakdown, ask for it in chat. For a saved or generated review, keep PRD requirements and WBS allocations in the same product model. The bundled schemas, scripts, and document references are available from an installed copy. [Product model](references/product-model.md) · [WBS process](references/wbs-process.md) · [Friction log](references/friction-log.md)

## Design and research

| Task | Skills |
| --- | --- |
| Build an interface | [frontend-design](skills/frontend-design/SKILL.md) · [design-system](skills/design-system/SKILL.md) |
| Recreate a reference | [image-to-code](skills/image-to-code/SKILL.md) · [url-to-code](skills/url-to-code/SKILL.md) |
| Assess a screen or implementation | [design-critique](skills/design-critique/SKILL.md) · [accessibility-review](skills/accessibility-review/SKILL.md) · [design-verification](skills/design-verification/SKILL.md) |
| Explore directions, plan a study, or write interface copy | [visual-exploration](skills/visual-exploration/SKILL.md) · [user-research](skills/user-research/SKILL.md) · [ux-copy](skills/ux-copy/SKILL.md) |

## Dart and Flutter

Use [dart-codegen](skills/dart-codegen/SKILL.md) for authoring or debugging generators, [dart-idioms](skills/dart-idioms/SKILL.md) for reviewing APIs and lifecycle choices, and [dartpad-examples](skills/dartpad-examples/SKILL.md) for a runnable teaching example.

| Package | When to use it | Example request |
| --- | --- | --- |
| [ack](skills/ack/SKILL.md) | Validate structured input with the Dart ACK schema library. | “Validate this API response with ACK and show how to report a missing field.” |
| [noir](skills/noir/SKILL.md) | Build or debug an interactive terminal UI using Dart Noir. | “Show the selected row in my Noir terminal list and handle keyboard navigation.” |
| [mix](skills/mix/SKILL.md) | Style Flutter widgets using Mix tokens, modifiers, and variants. | “Give this Mix-styled panel different padding at the compact breakpoint.” |
| [remix-flutter](skills/remix-flutter/SKILL.md) | Build a Flutter interface with Remix components and the project's theme or presets. | “Use our Remix buttons for this form and preserve the loading state.” |

Use one active provider for a given skill. If a separate package or specialist kit already supplies it, choose which installation to use. Flutter's official provider supplies general Dart and Flutter tasks and the Dart MCP server. [SDK setup](../../docs/external-plugins.md) · [Source credits](SOURCES.md)
