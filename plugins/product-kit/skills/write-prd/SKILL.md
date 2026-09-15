---
name: write-prd
description: Create or revise product, module, or feature PRDs with structured requirements, shared questions and decisions, validated JSON, and generated reviews. Includes Word/PDF references and optional connected WBS generation; not a general product-discovery or implementation workflow.
---

# Write PRD

<!-- Includes adapted review guidance from Leo's write-spec; see ../../SOURCES.md. -->

This skill defines the PRD workflow. The product-kit plugin bundles its
shared schema, examples, validators, queries, generators, and document references.
No external product or template plugin is required. Resolve the plugin
root two levels above this skill directory (../..); run commands from that root, not the
user's working directory.

## Define and review requirements

Read existing project evidence before asking for missing context. Identify whether
the scope is a product, module, or feature. Modules are optional; shared controls
do not need artificial features.

Establish the user problem, affected users, intended outcome, boundaries, and
assumptions. Make requirements observable, prioritize using the supplied convention,
and distinguish current, optional, deferred, and excluded scope. Review relevant
success measures, designs, dependencies, and failure, empty, permission, and boundary
cases. Unknown targets remain unknown; do not invent content to fill sections.

Preserve authoritative IDs and exact requirement wording. Separate supported facts,
proposed behavior, and unresolved decisions. Mark acceptance criteria Confirmed,
Proposed, or Not documented. Neither a reviewed requirement nor a generated PRD
proves implementation or authorizes a scope change.

Scale the review to the requested scope; do not expand a small feature into a full
product strategy. Inspect supplied APIs or schemas before asserting technical
contracts. Otherwise describe observable behavior and leave unsupported endpoints,
defaults, encodings, and status codes open or explicitly proposed. Before delivery,
trace acceptance criteria to evidence and check contradictions and adjacent scope
accidentally introduced by the draft.

## Create the structured record

Read [record conventions](../../references/record-conventions.md) for IDs, scope,
question fields, resolution/reopening, and machine-readable queries. Read
[the model contract](../../references/product-model.md) before authoring JSON. Use
[the schema](../../references/product.schema.json) and
[the fictional example](../../assets/examples/product/product.json) to populate a
separate project file, without inheriting example commitments, owners, or dates.

- Give each requirement one owning scope and explicit applicable scopes.
- Store each question once, linked to affected scopes and/or requirements.
  Store its resolution in a referenced decision, not duplicate answer fields.
- Keep maturity, evidence, acceptance confirmation, question resolution,
  validation result, and task progress independent.
- Set delivery to null until actual planning data exists. When delivery is
  requested, preserve primary/contributing package links and stage-level holds.
- Cite the actual source authority. Rendering input does not automatically
  replace the project's knowledge or decision system.

The current schema has limits, including structured success metrics and
scope-specific objective/owner fields. Do not silently drop supplied information
or claim complete capture when the schema cannot express it: identify the gap and
retain it in the accompanying review. Schema expansion is a separate change from
populating a PRD. See the model contract for all known limits.

## Validate, query, and generate

From the plugin root, with Python 3.10+ and uv:

```sh
uv run scripts/build_product.py /absolute/path/product.json --check
uv run scripts/build_product.py /absolute/path/product.json --out /absolute/path/review
uv run scripts/query_product.py /absolute/path/product.json questions --scope FEATURE-ID --status Open
uv run scripts/query_product.py /absolute/path/product.json questions --scope FEATURE-ID --unresolved
```

Substitute actual paths and IDs. The scripts declare their JSON-schema dependency.
Queries emit JSON; parse records, not rendered prose. Correct invalid source data
before generating. Open the output index.html and inspect affected PRDs, questions,
validation evidence, and traceability against supplied evidence. Structural
validation is not content approval. Regenerate all views after a shared edit.

Use --unresolved for a review of all unsettled questions, including assumptions;
--status Open deliberately excludes provisional decisions. Follow the same record
conventions when updating a question, rather than adding an answer to a PRD table.

Save deliverables outside the plugin. Return relevant files, unresolved gaps, and
checks performed. Do not create tickets, publish, or plan implementation merely
because a PRD exists.

## Word, PDF, and optional WBS

For Word/PDF deliverables or template maintenance, read
[document generation and references](../../references/document-generation.md).
The [PRD Word](../../assets/prd/reference.docx) and [PDF](../../assets/prd/reference.pdf)
references guide layout; they are manual-review snapshots, not the JSON contract.

For requested WBS work, use the sibling [write-wbs skill](../write-wbs/SKILL.md).
Read [the WBS process](../../references/wbs-process.md) for its data contract.
The product generator includes a connected WBS when delivery exists, using the
bundled WBS helper. It does not estimate work or invent dates. Do not maintain a
second requirement baseline for WBS when using the connected model.

## Maintain and verify

Keep schema, scripts, and instructions aligned. From the plugin root:

```sh
uv run --with jsonschema==4.26.0 python -m unittest discover -s scripts/tests -v
```

For packaging changes, copy the complete plugin outside the repository and test validation,
queries, and generation there. Render and visually inspect changed Word references;
unchanged retained assets need not be regenerated.
