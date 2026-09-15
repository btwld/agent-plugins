# Product and open-question record conventions

This is the product-kit plugin's version-1 convention, not a claimed
Atlassian, Anthropic, or industry data standard. The
[JSON schema](product.schema.json) defines field shapes; the
[model validator](../scripts/product_model.py) additionally checks references and
cross-record rules. Use both through the CLI before consuming records.

## Identity and scope

| Record | Meaning | Suggested new-ID prefix |
| --- | --- | --- |
| Product | Overall problem and product boundary | PROD- |
| Module | Optional group of capabilities within a product | MOD- |
| Feature | User capability, under a product or module | FEAT- |
| Requirement | Independently identifiable expected behavior or constraint | REQ- |
| Question | One independently answerable uncertainty | OQ- |
| Decision | Recorded resolution or provisional choice | DEC- |
| Validation | Criterion and observed result/evidence | VAL- |
| Source | Reference to the evidence supporting records | SRC- |

Prefixes are authoring suggestions, not parser rules. Preserve existing source IDs;
do not renumber records when their order, wording, owner, or parent changes. Core
record IDs are case-sensitive and unique across these collections. They match
`^[A-Za-z0-9][A-Za-z0-9._-]*$`; names and prose are separate fields. Workflow step
IDs are local to a feature; delivery IDs use their own collections.

A requirement's `scope_id` is its one owning scope. `applies_to` explicitly lists
applicable scopes, each including descendants. Ownership is not applicability:
a product-owned requirement may apply only to selected features. A PRD is a view
over those records, not another copy to edit. See [scope selection](product-model.md).

## Standard question record

This complete question record comes from the fictional example; it belongs in
the full product model, where its requirement and source references resolve:

```json
{
  "id": "OQ-001",
  "text": "Which roles may change operating records and view the corresponding totals?",
  "owner": "Unassigned",
  "scope_ids": [],
  "requirement_ids": ["REQ-002", "REQ-003", "REQ-004"],
  "status": "Open",
  "decision_id": null,
  "source_ids": ["SRC-EXAMPLE"]
}
```

| Field | Convention |
| --- | --- |
| `id` | Stable question identity; never derive it from the current row number |
| `text` | A question with an answer that can be recorded; split independently answerable uncertainties |
| `owner` | Accountable answer owner, or the literal `Unassigned` when unknown |
| `scope_ids` | Affected product/module/feature IDs; useful before requirements exist |
| `requirement_ids` | Affected requirements, zero or more; one question may affect several |
| `status` | Exactly `Open`, `Answered`, or `Assumed` |
| `decision_id` | Null for Open; an existing decision ID for Answered or Assumed |
| `source_ids` | At least one evidence reference; an honest draft/source record is not proof of confirmation |

All fields are required. At least one of `scope_ids` or `requirement_ids` must be
nonempty. Arrays contain IDs, not comma-separated strings; use `[]` for no links,
and JSON `null` for no resolution, not the text "null". Unknown extra fields,
duplicate keys, duplicate IDs, unsupported states, and dangling references fail
validation. Do not embed an independent `answer` field in a requirement or question.

## Answering, assumptions, and reopening

1. For an answer, add or reference a decision with its outcome, rationale, owner,
   and source evidence; set the question's decision ID and status to Answered.
2. For a provisional choice, reference a decision but use Assumed. It remains an
   unresolved question; it is not equivalent to a confirmed answer.
3. To reopen, set status to Open and decision ID to null. Preserve earlier decision
   evidence in the project authority; do not erase or rewrite it to hide the change.
4. Review affected requirements against the decision. Do not automatically change
   their statements, maturity, acceptance confirmation, or validation results.
5. Revalidate and regenerate all affected document views from the same source.

An answer's timestamp and full state history are not modeled in version 1. Retain
them in the cited authority when needed; do not insert unrecognized JSON fields or
pretend the plugin stores an audit trail. A future version can add that contract.

## Blockers are relationships

A question is not globally blocking just because it is open. With delivery data,
`question_dependencies` links it to a package and scheduled stage, plus a `blocking`
flag and reason. A blocking Open or Assumed question holds that stage. Answered
clears the decision hold only. No delivery data means no encoded schedule hold,
not proof that implementation has no blockers.

`--status Open` returns only unanswered questions with no provisional decision.
Use `--unresolved` to include both Open and Assumed; the flags are mutually exclusive.

## Consume records without parsing documents

From the plugin root:

```sh
uv run scripts/query_product.py assets/examples/product/product.json product
uv run scripts/query_product.py assets/examples/product/product.json modules
uv run scripts/query_product.py assets/examples/product/product.json features --scope MOD-OPS
uv run scripts/query_product.py assets/examples/product/product.json requirements --scope FEAT-WORKFLOW
uv run scripts/query_product.py assets/examples/product/product.json questions --scope MOD-OPS --unresolved
```

Every result is a JSON array retaining original records. Product returns the one
root record; module/feature queries select records in the requested subtree.
Requirement/question selection also includes relevant shared records. Resolve
links against the complete source, since a filtered result is not a standalone
product model. Empty results are `[]`; errors go to stderr with a nonzero exit.

Both product and standalone WBS input use the shared strict JSON decoder. Shared
product validation then applies schema and reference checks. Standalone WBS uses
its own documented contract and is not a second place to maintain shared questions.
