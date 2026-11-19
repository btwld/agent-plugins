---
name: write-wbs
description: Create or review a delivery work breakdown from supplied requirements. Return work packages and dependencies in chat, update a connected product model, or generate a standalone scheduled review as requested.
---

# Write WBS

## Break down the work

Read the requirements and planning evidence. Preserve requirement IDs and wording. Group work by deliverable. For each package identify its outcome, owner if known, dependencies, completion evidence, and disposition. Give each requirement exactly one primary package, including deferred or excluded scope. Additional contributing packages can share the work.

For a quick breakdown, return the packages, their primary IDs, and open inputs in chat. Leave unknown owners and dates open. A package assignment does not commit a team to a schedule. Use [write-prd](../write-prd/SKILL.md) when the requested decision is about product behavior. Use Engineering Kit's `writing-plans` for implementation steps once requirements are settled.

## Save or generate a review when requested

Resolve the product-kit root two levels above this skill's directory. Read the [WBS process](../../references/wbs-process.md) for planning fields, stage and release semantics, generation, and validation.

- **Connected product record.** Update its delivery section against the [product model](../../references/product-model.md) and [shared record conventions](../../references/record-conventions.md). Reuse requirement, question, decision, and validation IDs. Keep primary and contributing assignments distinct. Link blocking questions to the affected stages. Open or Assumed questions retain their holds. A resolved decision or completed task still needs its own validation evidence.
- **Standalone scheduled plan.** Use the [example plan](../../assets/examples/wbs/plan.json) for structure. Populate a separate project file using the supplied schedule, dependencies, and gates. Keep stages, releases, and dates distinct.
- **Unscheduled review.** Use the requested text or document format. With no actual schedule, leave a new product model's delivery section null. Preserve existing schedules. The timeline generator needs dates. If Word or PDF is requested, consult the [document guide](../../references/document-generation.md), [Word reference](../../assets/wbs/reference.docx), and [PDF reference](../../assets/wbs/reference.pdf).

Run the relevant pair from the plugin root using the actual source and a separate output directory.

```sh
# Connected model
uv run scripts/build_product.py /absolute/path/product.json --check
uv run scripts/build_product.py /absolute/path/product.json --out /absolute/path/review

# Standalone scheduled plan
python3 scripts/build_wbs.py /absolute/path/plan.json --check
python3 scripts/build_wbs.py /absolute/path/plan.json --out /absolute/path/review
```

For standalone PDF output, add `--pdf` to the generation command and provide Chrome or Chromium. Python 3.10+ is required. The connected generator declares its schema dependency through uv.

Resolve coverage gaps, broken references, cycles, and inconsistent dates in the source before generation. Inspect the resulting package coverage, dependencies, schedule, and any stage holds against the supplied baseline. Inspect each PDF page before sharing. Report the requested deliverable, remaining planning gaps, and checks performed. Drafting a WBS alone does not authorize creating tickets, publishing, or starting implementation.
