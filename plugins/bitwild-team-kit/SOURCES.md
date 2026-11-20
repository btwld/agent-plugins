# Bitwild Team Kit sources and licenses

The following sections retain attribution by former kit. See the Product section for company generators and document assets.

## Engineering

This file records origins and licenses only. The kit is maintained directly in
this repository.

Skills, helpers, and fixtures derive from [Leo Farias's skills](https://github.com/leoafarias/skills),
`plugins/engineering-kit`, commit `fce84a2eb288ee43e8a7160f30f2fd3fb7931187`.

| Content | Earlier source and baseline | License |
| --- | --- | --- |
| `architecture` | [Anthropic Knowledge Work](https://github.com/anthropics/knowledge-work-plugins), `engineering/skills/architecture`, `d463f6f0dce59a99c4869598324aac25b28ad4f9` | [Apache-2.0](licenses/knowledge-work-Apache-2.0.txt) |
| `writing-plans`, `executing-plans` | [Superpowers](https://github.com/obra/superpowers), respective `skills/` directories, `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | [MIT](licenses/superpowers-MIT.txt) |
| `code-simplifier` | [Anthropic Code Simplifier](https://github.com/anthropics/claude-plugins-official), `plugins/code-simplifier/agents/code-simplifier.md`, `ceb9b72b4c4c20ad39efce780edd0aabe80ebce3` | [Apache-2.0](licenses/anthropic-code-simplifier-Apache-2.0.txt) |
| `ci-loop`, `pr-canvas`, `pr-comments`, `pr-authoring` (includes the former `pr-prep` history preparation), `verify` | [Cursor Plugins](https://github.com/cursor/plugins), `cursor-team-kit/skills/`, `ddf824aff1e55ba14bd666b30bce3fc69962abe6` | [MIT](licenses/cursor-team-kit-MIT.txt) |
| `writing-for-agents` | [Matt Pocock Skills](https://github.com/mattpocock/skills), `writing-for-agents`, `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d` | [MIT](licenses/mattpocock-skills-MIT.txt) |
| Remaining engineering skills and local adaptations | Leo Farias | [BSD-3-Clause](licenses/leo-kit-BSD-3-Clause.txt) |

The PR authoring and architecture revisions adapt the corresponding Leo Skills
workflows at `29f785013573715f2a9575901fcfea6c16af9c9a`.

Deep Code Review and the explicitly callable Test Audit use Leo Farias's local
1.0.0 workflow revisions (BSD-3-Clause). The existing company review helpers
remain bundled with Deep Code Review.

Concepta's publisher metadata does not replace the original copyright notices.
No external source repository or plugin is required to run these skills.

## Product

This file records origins and licenses only. The kit is maintained directly in
this repository.

### Skill sources

The research skills and selected PRD review guidance derive from
[Leo Farias's skills](https://github.com/leoafarias/skills),
`plugins/product-kit`, commit `08bc3fbb6fe738d48604828262be47382c5879b7`.

| Content | Earlier source | License notices |
| --- | --- | --- |
| `product-brainstorming`, `research-synthesis`, `competitive-brief`, selected `write-prd` guidance | Leo's adaptations of [Anthropic Knowledge Work](https://github.com/anthropics/knowledge-work-plugins), baseline `d463f6f0dce59a99c4869598324aac25b28ad4f9` | [BSD-3-Clause](licenses/leo-kit-BSD-3-Clause.txt), [Apache-2.0](licenses/knowledge-work-Apache-2.0.txt) |
| `ux-friction-research` | Leo's original skill | [BSD-3-Clause](licenses/leo-kit-BSD-3-Clause.txt) |

No OpenAI package content is included. These notices cover their respective
adapted material; they do not assign a blanket license to the company code or
reference assets.

### Document references

The generalized PRD and WBS presentation references derive from previously
reviewed requirement and work-breakdown reference documents and their renderers.
They are layout adaptations, not client records or pixel-identical reproductions.
The JSON schema and generators are the company implementation; no external
workspace is required to use them.

## Design

Maintained independently by Concepta. Attribution below records origins, not an
update, import, or synchronization workflow. Original adaptations are by Leo Farias.

| Skills | Origin | License |
| --- | --- | --- |
| accessibility-review, user-research, design-critique, ux-copy, design-system | anthropics/knowledge-work-plugins, design/skills, baseline d463f6f0dce59a99c4869598324aac25b28ad4f9 | Apache-2.0 |
| frontend-design | anthropics/claude-plugins-official, plugins/frontend-design/skills/frontend-design, baseline 3b600518a637492d37c9877aeb49c2a55d939c04 | Apache-2.0 |
| design-verification, visual-exploration, image-to-code, url-to-code | Original Leo Farias skills | BSD-3-Clause |

The original skills were informed by reference-only review of OpenAI's proprietary
product-design 0.1.55 package; no package content is included or licensed here.

Retained notices: [BSD license](licenses/leo-kit-BSD-3-Clause.txt), [Knowledge Work Apache license](licenses/knowledge-work-Apache-2.0.txt),
[Frontend Design Apache license](licenses/anthropic-frontend-design-Apache-2.0.txt),
and [Frontend Design notice](skills/frontend-design/LICENSE.txt).

## Dart packages

The four package workflows are original and distributed under [BSD-3-Clause](licenses/leo-kit-BSD-3-Clause.txt). The package teams maintain the detailed APIs, examples, and guides. The following revisions identify the documentation reviewed for these workflows.

| Package | Sources reviewed |
| --- | --- |
| ACK | [ACK LLM guide](https://github.com/btwld/ack/blob/b8eb8ebc9887cccaf21b7fe97a08fadc2839d0ba/llms.txt) · [published versions](https://pub.dev/packages/ack/versions) |
| Noir | [Noir terminal skill and references](https://github.com/btwld/noir/tree/1924c3ac3625dcf2f01c1b83a28ac1adb61ee12a/skills/noir) · [0.0.7 demo recording](https://github.com/btwld/noir/tree/noir-v0.0.7/skills/record-noir-demo) · [published versions](https://pub.dev/packages/noir/versions) |
| Mix | [Mix skill and references](https://github.com/btwld/mix/tree/e5259d8e65a32f7b7f11d14e6d734fe76226f8e6/skills/mix) · [published versions](https://pub.dev/packages/mix/versions) |
| Remix | [Remix usage and design-system skills](https://github.com/btwld/remix/tree/a3642ff2030efd42c1ecda9c3848e61fc7770f48/skills) · [RC.5 registry authoring](https://github.com/btwld/remix/tree/remix-v1.0.0-rc.5/skills/building-remix-design-system) · [published versions](https://pub.dev/packages/remix/versions) |

### Dart specialist skills

The `dart-codegen`, `dart-idioms`, and `dartpad-examples` directories come from
Leo Farias's audited 1.0.0 Dart Flutter Kit, commit
`ef61e69d469b9d87f95c4fbe1fb09a9fe4d4e569`. The first two use the
[BSD-3-Clause notice](licenses/leo-kit-BSD-3-Clause.txt). DartPad Examples
includes its own [license](skills/dartpad-examples/LICENSE).
