# Structured product reviews

One input generates product, module, and feature PRDs, a shared question/decision
register, delivery traceability, and the existing WBS timeline. This is a reusable
template contract, not an approved Element product model.

For the exact authoring conventions and question lifecycle, read
[record conventions](record-conventions.md). These are local plugin conventions,
not an external PRD data standard.

## Structure

```text
Product → optional Module → Feature
Requirement → one owning scope + explicit applicable scopes
Question → affected scopes and/or requirements → resolution Decision
Validation → requirements → evidence or explicit waiver
Requirement → one primary WBS package + optional contributing packages
Task → package + requirement references
Question → explicit dependency on a package's scheduled stage
```

A feature is a capability; a requirement is an identifiable commitment; a WBS
package is a deliverable. Requirements usually describe feature behavior, but
product-wide controls and module-wide rules need not become artificial features.
Multiple requirements can feed one package; one requirement can need several
packages. A feature may belong directly to the product when no module is useful.

### Ownership and applicability

`scope_id` is a requirement's owning product, module, or feature. `applies_to`
explicitly lists where it applies; each listed scope includes its descendants.
Product ownership alone does **not** imply global applicability.

A PRD includes requirements owned within its subtree plus applicable shared
requirements. Product views roll up the baseline; module and feature views select
relevant records without changing their IDs or exact wording. Count unique IDs,
not appearances across documents. Contributing work does not automatically change
a requirement's product applicability.

### Shared questions and independent states

A question can affect several requirements or a scope before requirements exist.
Its answer lives once in a referenced decision, not in duplicate answer fields.

| Question state | Meaning |
| --- | --- |
| Open | No resolution; `decision_id` is null |
| Answered | A recorded decision resolves the question |
| Assumed | A provisional decision, not a confirmed answer |

Only explicit `blocking` dependencies hold a WBS stage. Both Open and Assumed
retain that hold. Answered clears the decision hold, not verification.

Keep requirement maturity, evidence support, acceptance confirmation, release
disposition, question resolution, validation result, and task progress separate.
Acceptance criteria are Confirmed, Proposed, or Not documented; missing criteria
are an empty list, not invented filler. Answering a question does not confirm
criteria. Completing tasks does not pass validation. Passed/Failed validations
require evidence references; Not required needs a waiver reason. Missing
validation means unknown, not passed.

## Files and commands

| File | Role |
| --- | --- |
| [product.schema.json](product.schema.json) | Versioned fields, types, and allowed states |
| [product.json](../assets/examples/product/product.json) | Fictional working example, not client evidence |
| [product_model.py](../scripts/product_model.py) | References, scope selection, lifecycle rules, WBS adapter |
| [build_product.py](../scripts/build_product.py) | Connected HTML and Markdown views |
| [query_product.py](../scripts/query_product.py) | Validated JSON records for other tools |
| [json_io.py](../scripts/json_io.py) | Strict JSON decoding shared by PRD and standalone WBS inputs |

Run from the repository root:

```sh
uv run plugins/product-kit/scripts/build_product.py plugins/product-kit/assets/examples/product/product.json --check
uv run plugins/product-kit/scripts/build_product.py plugins/product-kit/assets/examples/product/product.json --out .context/product-review
uv run --with jsonschema==4.26.0 python -m unittest discover -s plugins/product-kit/scripts/tests -v
```

Open `.context/product-review/index.html`. Each PRD and register has HTML and
Markdown versions. The WBS HTML reuses the existing timeline and includes the new
contribution, task, question-dependency, and validation relationships. Browser
Print / Save PDF exports a view; check pagination before sharing.

Edit the input and regenerate, not the generated documents. The output manifest
tracks generator-owned files: regeneration overwrites these and removes retired
views, leaving unrelated files alone. Separately exported PDFs are snapshots that
need manual refresh. Views carry the input's SHA-256 fingerprint.

Copy the example outside the template folder for a real product; replace its
fictional values with sourced records. Update or omit the optional relative
`$schema` path after moving it; the CLI uses the repository schema. Set
`delivery: null` until an actual plan exists: PRDs generate without invented dates.
With delivery present, every requirement needs one primary allocation, including
unscheduled later/optional/excluded buckets. Primary and contributing packages
must match the requirement's disposition; split mixed-disposition work. Dates and
dependencies follow the [existing WBS contract](wbs-process.md).

The JSON is the single rendering input, not automatically the project's knowledge
authority. Preserve exact authoritative requirements and their source references.
Changes to real knowledge still follow the knowledge-bundle workflow.

## Read records programmatically

Requirements, questions, decisions, and validations are JSON arrays in the input,
not fields to extract from prose. Stable `id` values join records. Requirement
`scope_id` and `applies_to` identify ownership and applicability; a question's
`requirement_ids` and `scope_ids` identify affected records, and `decision_id`
references its resolution. These field names and allowed values are defined in
the version-1 schema, with cross-reference checks in the model validator.
The query interface also exposes the product record (as a one-element array),
modules, and features. Module and feature queries select the requested subtree.

```sh
# All requirements, preserving every field and exact wording.
uv run plugins/product-kit/scripts/query_product.py plugins/product-kit/assets/examples/product/product.json requirements

# Requirements relevant to one module, including applicable shared controls.
uv run plugins/product-kit/scripts/query_product.py plugins/product-kit/assets/examples/product/product.json requirements --scope MOD-OPS

# Only open questions relevant to one feature.
uv run plugins/product-kit/scripts/query_product.py plugins/product-kit/assets/examples/product/product.json questions --scope FEAT-WORKFLOW --status Open

# All unsettled questions, including provisional assumptions.
uv run plugins/product-kit/scripts/query_product.py plugins/product-kit/assets/examples/product/product.json questions --scope FEAT-WORKFLOW --unresolved

# Retrieve resolution records and implementation evidence independently.
uv run plugins/product-kit/scripts/query_product.py plugins/product-kit/assets/examples/product/product.json decisions --scope MOD-OPS
uv run plugins/product-kit/scripts/query_product.py plugins/product-kit/assets/examples/product/product.json validations --scope MOD-OPS
```

The query command validates the complete input first, then writes only a JSON
array to stdout. No matches returns `[]`; errors go to stderr with a nonzero exit
code. Query results preserve original records and links, including links to scopes
outside the selected view. They are filtered projections, not standalone product
models; resolve their references against the full validated input. Product-level
decision queries return all decisions; narrower queries return decisions referenced
by that scope's relevant questions.

Both generation and queries reject duplicate JSON keys and nonstandard numeric
constants, in addition to schema errors and broken links. This prevents silent
overwriting of fields such as a question's status. For direct Python use, call
`product_model.parse_product(raw_json)` before reading records. Do not treat a plain
`json.loads()` call as schema or relationship validation. Query output is generated
data; edit the original source and rerun rather than keeping another editable copy.

## Templates and skills

| Piece | Responsibility |
| --- | --- |
| `write-prd` | Author and review product, module, or feature requirements |
| `write-wbs` | Build delivery breakdowns from the same requirement baseline |
| JSON schema and validators | Define and check machine-readable records and relationships |
| Generators and query tools | Produce connected reviews and JSON projections |
| Word/PDF references | Guide presentation; they are not the record format |

The Product Kit owns this contract and its shared helpers. Other skills can
complement a requested review but are not dependencies. Product, module, and
feature views do not need separate skills or separate requirement baselines.

## Validation and limitations

The example has eight requirements, three questions, two decisions, two pending
validations, eight primary allocations, and two explicit stage holds. Tests cover:

- Correct scope selection, shared requirements, optional modules, and no-schedule PRDs.
- One question edit propagating into all affected generated documents.
- Assumptions retaining holds; decisions and tasks not passing validations.
- Rejection of broken references, duplicate/missing allocations, and unknown fields.
- Proposed versus undocumented acceptance, exact wording, and escaped source text.
- Existing WBS date, dependency, and primary-coverage checks.
- Removal of retired generated views without deleting unrelated files.

These checks prove structural consistency and generation behavior for the supplied
data, not real baseline completeness, approval, acceptance quality, effort, or
release readiness. Evidence references must still be read and assessed. The schema
does not yet model nested modules, feature dependencies, revision history,
structured success metrics, or approval workflows. Add such records when actual
source material and a concrete use case require them, not to fill a template.

## Design trade-off

| Approach | Fit |
| --- | --- |
| Parse filled Word/Markdown | Retains manual editing, but headings and duplicate answers are fragile machine interfaces |
| Nest every record under features | Simple locally, but duplicates shared requirements and questions |
| Shared records and generated views | Chosen: stable IDs and testable relationships; requires maintaining a schema and generator |

Revisit storage if an authoritative tracker or knowledge system supplies these
records: adapt that source instead of keeping a second editable database. Revisit
the hierarchy if real scope needs additional levels; do not invent grouping to
satisfy this example.
