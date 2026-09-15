# Product Kit

A Codex and Claude Code plugin for product exploration, evidence-backed research,
structured requirements, and connected delivery planning. It does not independently
approve scope, invent estimates, or turn research findings into commitments.

| Skill | Use |
| --- | --- |
| [product-brainstorming](skills/product-brainstorming/SKILL.md) | Explore problems, alternatives, assumptions, and product opportunities |
| [research-synthesis](skills/research-synthesis/SKILL.md) | Turn supplied research and customer feedback into traceable findings |
| [competitive-brief](skills/competitive-brief/SKILL.md) | Compare alternatives for positioning and build-versus-buy decisions |
| [ux-friction-research](skills/ux-friction-research/SKILL.md) | Investigate public user difficulties or review an existing friction log |
| [write-prd](skills/write-prd/SKILL.md) | Product, module, and feature PRDs with structured requirements, questions, and decisions |
| [write-wbs](skills/write-wbs/SKILL.md) | Work packages, primary/contributing coverage, stages, releases, dependencies, and WBS reviews |

The PRD/WBS skills share one set of scripts, reference guides, schema, example JSON, and
Word/PDF assets at the plugin root. There are no copies to keep synchronized.
The connected product model remains the single rendering input for PRD and WBS.

## Working process

Select the skill that matches the request. Exploration and research can inform a
PRD, but are not mandatory prerequisites. A supplied requirement baseline can go
straight to PRD review or WBS planning. Competitive research compares alternatives;
friction research assesses user difficulties; synthesis analyzes supplied evidence.
Choose the requested workflow without imposing a fixed sequence.

For requirements and delivery work:

1. Read the actual evidence and identify the product, module, or feature boundary.
2. Define the intended outcome, scope, and observable requirements; keep unknowns visible.
3. Record requirements and shared questions using stable IDs and the record conventions.
4. Review decisions and acceptance criteria without confusing agreement with implementation proof.
5. Validate the source and generate the PRDs and question/decision views.
6. When delivery planning is requested, add WBS allocations and real scheduling inputs
   to the same model; validate and regenerate the connected review.

The shared model is the source for generated PRDs and WBS reviews. Research
informs its records but does not automatically populate them. Post-launch
measurement is not a PRD generator function.

## Friction research versus a friction log

Research is the evidence-gathering and assessment workflow. A friction log is a
project artifact that records findings, evidence, verification, disposition, and
next checks. `ux-friction-research` can create or review it; `research-synthesis`
can contribute findings from supplied studies. A reported problem is not a
reproduced bug, and a finding is not an approved requirement.

Use the [shared log convention](references/friction-log.md) when requested. Preserve
existing project records rather than creating competing lists. The log is not a
new product-schema record and is not validated by the PRD JSON validator.

## Use

After installation, start a new thread and ask to use
`product-kit:write-prd` or `product-kit:write-wbs`, supplying the relevant
source material. Claude Code also exposes `/product-kit:write-prd` and
`/product-kit:write-wbs`. See the [repository installation guide](../../README.md).
The other skills use the same namespace, for example
`/product-kit:ux-friction-research`. Choose one skill for the requested outcome;
installing the kit does not run all six workflows.

From this plugin directory:

```sh
uv run scripts/build_product.py assets/examples/product/product.json --check
uv run scripts/build_product.py assets/examples/product/product.json --out /absolute/path/product-review
uv run scripts/query_product.py assets/examples/product/product.json questions --status Open
python3 scripts/build_wbs.py assets/examples/wbs/plan.json --check
python3 scripts/build_wbs.py assets/examples/wbs/plan.json --out /absolute/path/wbs-review
uv run --with jsonschema==4.26.0 python -m unittest discover -s scripts/tests -v
```

Requirements: Python 3.10+ and uv for dependency-managed product commands.
Word-reference rebuilding uses python-docx through the documented uv command;
WBS PDF export needs Chrome/Chromium. No MCP server, credentials, or other product
plugin is required. Document apps can be used when Word/PDF editing is requested.

See [the model contract](references/product-model.md),
[record conventions](references/record-conventions.md),
[WBS contract](references/wbs-process.md), and
[document references](references/document-generation.md). Retained Word/PDF
templates guide presentation; the schema defines machine-readable records.
See the model contract for fields and limitations.

## Maintenance

Edit canonical files in `plugins/product-kit/`, not installed caches. Keep schema,
generators, references, and skill instructions aligned. Run the checks above and
the repository packaging checks for changes. Save real project records and generated
output outside the plugin.

Included evaluation fixtures support behavioral review; their presence is not a
claim that an evaluation was run. Source and license notices are in
[attribution](SOURCES.md). Release versions are recorded in the provider manifests.
