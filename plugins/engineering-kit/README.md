# Engineering Kit

Engineering workflows for Codex and Claude Code, installed as
`engineering-kit@conceptadev`. The kit has 16 workflows and two compatibility commands.

## Choose a workflow

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

Product Kit owns PRDs, requirements/questions, and WBS delivery breakdowns.
Engineering planning turns settled scope into implementation steps; it does not
create another requirement baseline. Neither kit requires automatic handoffs.
Dart/Flutter capabilities come from the external official provider, not this kit.

## Install and use

Follow the [repository setup](../../README.md), then use the matching command:

```sh
codex plugin add engineering-kit@conceptadev
claude plugin install engineering-kit@conceptadev
```

These are alternative clients; install only where needed. Start a new session
afterward. Claude namespaced skills include `/engineering-kit:architecture` and
`/engineering-kit:writing-plans`; in Codex ask to use the relevant skill.
Choose one active provider for this plugin namespace. Maintaining this repository
does not replace installed plugins. The skills are self-contained; source and
license notices are retained in [attribution](SOURCES.md).

## Helpers and validation

Resolve helpers from the loaded skill directory, not the project being reviewed.
Python 3.10+ is required; SBVR YAML parsing additionally needs PyYAML. Browser
verification uses the host's available browser tools or the project's test setup;
it does not install a browser backend as a side effect.

From this plugin directory:

```sh
python3 -m unittest discover -s tests -v
python3 skills/sbvr/scripts/validate.py skills/sbvr/examples/streaming-service-sbvr.md --json
```

Run repository packaging checks for a release and test helpers from an isolated
copy after packaging changes. Included skill eval fixtures support behavioral
review; structural validation and passing helper tests do not prove model behavior.
Keep generated review output and real project records outside the plugin.
