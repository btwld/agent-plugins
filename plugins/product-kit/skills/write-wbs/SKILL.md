---
name: write-wbs
description: Create or revise a work breakdown structure and delivery review from a requirement baseline and planning evidence, with package definitions, primary coverage, lifecycle stages, releases, dependencies, and optional timeline/PDF generation. Not a PRD-authoring or automatic estimation workflow.
---

# Write WBS

Use the product-kit plugin's shared resources. Resolve the plugin root two
levels above this skill directory (../..); run commands from that root.
Read [the WBS contract](../../references/wbs-process.md) before changing plans.
For linked requirements and questions, follow the shared
[record conventions](../../references/record-conventions.md); do not create
WBS-specific copies of their identities or answers.

## Select the source

- If a product JSON model exists, read [the product contract](../../references/product-model.md)
  and maintain its delivery section. Requirements, questions, decisions, and
  validations remain shared records; do not copy them into another editable plan.
- For a standalone WBS baseline, use [the example plan](../../assets/examples/wbs/plan.json)
  as a structural reference. Populate a separate project file from actual sources.
- If the request is to define product behavior first, use
  [write-prd](../write-prd/SKILL.md); do not invent requirements to fill packages.

Check scope and source evidence. Preserve requirement IDs and wording. Identify
unknown owners, missing scheduling information, and unresolved questions explicitly.
No package, timeline, or generated document constitutes scope approval.

## Build the breakdown

Group outcome-based work packages; grouping need not reproduce the feature tree.
For each package identify its deliverable, owner, completion evidence, dependencies,
and disposition. Assign each supplied requirement to exactly one primary package,
including unscheduled optional/deferred/excluded buckets. In the connected model,
record additional contributing packages without duplicating primary coverage.

Keep work groups, lifecycle stages, releases, and dates distinct. Use only supplied
or explicitly proposed planning values and label their status. Never invent dates
to satisfy validation. With no actual schedule, retain delivery as null in the PRD
and produce a manual unscheduled WBS using the retained reference; the scheduled
generator requires complete dates. Do not discard an existing schedule to switch modes.

For connected plans, link blocking questions to actual package stages. Open and
Assumed questions retain explicit holds. Answered resolves the decision hold,
not verification. Completed tasks do not imply passed validation or release gates.

## Validate and generate

From the plugin root, replace example paths with the actual source and a separate
output directory:

```sh
# Connected PRD and WBS from one source:
uv run scripts/build_product.py /absolute/path/product.json --check
uv run scripts/build_product.py /absolute/path/product.json --out /absolute/path/review

# Standalone WBS:
python3 scripts/build_wbs.py /absolute/path/plan.json --check
python3 scripts/build_wbs.py /absolute/path/plan.json --out /absolute/path/review --pdf
```

Python 3.10+ is required. The connected generator declares its JSON-schema
dependency through uv. Standalone validation/HTML use the standard library;
--pdf needs Chrome/Chromium and uses an isolated browser profile.

Resolve invalid references, coverage gaps, dependency cycles, and date errors
before generation. Check supplied baseline completeness against evidence separately.
Inspect hierarchy, package definitions, chronology, stages, releases/gates, and
coverage. For a connected plan, also inspect contributors, task links, question
holds, and validation states. Inspect every PDF page before sharing.

## Word references and maintenance

Use [document-generation guidance](../../references/document-generation.md),
[WBS Word](../../assets/wbs/reference.docx), and
[WBS PDF](../../assets/wbs/reference.pdf) for manual layout. Generated project
documents stay outside the plugin. Update source records and regenerate views;
do not edit generated HTML as an independent plan.

Shared tests run from the plugin root:

```sh
uv run --with jsonschema==4.26.0 python -m unittest discover -s scripts/tests -v
```

Return the requested review, missing planning inputs, and checks performed.
Do not create tracker tickets, publish, or start implementation merely because a
WBS has been drafted.
