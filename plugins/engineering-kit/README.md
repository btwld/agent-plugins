# Engineering Kit

Engineering workflows for Codex and Claude Code, installed as
`engineering-kit@conceptadev`. The kit contains 11 focused skills and their helpers.

## Skills

| Skill | Outcome |
| --- | --- |
| [architecture](skills/architecture/SKILL.md) | A grounded technical choice or architecture decision record |
| [writing-plans](skills/writing-plans/SKILL.md) | An executable implementation plan from settled requirements |
| [executing-plans](skills/executing-plans/SKILL.md) | Carry out an existing authorized implementation plan |
| [webapp-verification](skills/webapp-verification/SKILL.md) | Browser evidence and appropriate regression coverage |
| [pull-request-authoring](skills/pull-request-authoring/SKILL.md) | A grounded PR title/body and authorized PR creation or update |
| [adversarial-change-review](skills/adversarial-change-review/SKILL.md) | An evidence-backed keep/reject judgment on a particular change |
| [ai-slop-review](skills/ai-slop-review/SKILL.md) | Validated findings about unnecessary generated-code patterns |
| [clean-sheet-review](skills/clean-sheet-review/SKILL.md) | Reconsider an existing solution's scope and design |
| [code-simplifier](skills/code-simplifier/SKILL.md) | Explicitly requested behavior-preserving refinement |
| [reference-implementation](skills/reference-implementation/SKILL.md) | A canonical implementation suitable for reuse |
| [sbvr](skills/sbvr/SKILL.md) | Structured business vocabulary and rules |

Choose a skill for the requested outcome. Routine coding and reviews need no
wrapper workflow. `code-simplifier` retains explicit-only invocation, including
its Codex invocation policy. Other workflows keep their existing scope boundaries.

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
