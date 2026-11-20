# Product requirements review

[Project name] [Release or scope]

This document presents the proposed product scope for review. Review each module's workflow, requirements, and unresolved gates before recording a response. This is a review draft, not an approved baseline.

## Document control

| Field | Value |
| --- | --- |
| Project and release | [Project and release] |
| Prepared | [Date] |
| Status | [Draft or recorded approval status] |
| Version and source baseline | [Version and authoritative source reference] |
| Coverage | [Module count and requirement count derived from source] |
| Target release | [Planning target and commitment status] |
| Owner | [Named owner or Unassigned] |
| Reviewers and approver | [Names or Unassigned] |
| Return by and to | [Date and recipient] |

## How to review

Read one complete module packet at a time. Check the workflow, inspect the supporting diagram where available, confirm the exact requirements, and record one module response. Keep release position, evidence status, decision status, validation status, and requirement maturity distinct.

## Objective

[Explain the business problem, who is affected, the intended outcome, the product boundary, and what remains owned by another system or team. Cite the scope authority. Do not infer replacement or integration scope from the reference project.]

## Assumptions

| Assumption | Source and owner | Condition that invalidates it |
| --- | --- | --- |
| [Documented assumption] | [Reference and accountable owner] | [Trigger for review] |

## Product modules

Group the project's actual modules into meaningful parts. Repeat the following packet for each module. Include required reporting, platform, data, conversion, and cross-module controls in the review body when they are in scope; do not hide them in an optional appendix. Retain stable module identifiers.

### Module [ID] [Name]

[Describe the module's responsibility and boundary.]

Controlled coverage: [Source-derived total and counts by disposition].

#### How the work runs

Workflow [ID and name]

[State its purpose, trigger, actors, and preconditions.]

1. [Actor performs an action on a business object; state the resulting transition and handoff.]
2. [Next actor performs the next action; state any exception or approval path.]
3. [State completion, retained evidence, and the downstream handoff.]

Still to settle: [Linked decision or validation gates, accountable owners, and closure evidence. If none, say none documented.]

#### Visual reference

[Insert a sourced diagram of this workflow or boundary and a descriptive caption. Label whether it is a workflow, system boundary, or approved screen design. Omit the image if none is available; do not invent a UI commitment.]

#### Controlled requirements

| Requirement | Exact commitment | Workflow step | Priority and release | WBS package | Maturity and gates |
| --- | --- | --- | --- | --- | --- |
| [ID and title] | [Verbatim authoritative statement] | [Workflow and step] | [Separate priority and disposition] | [Primary package ID] | [Maturity and linked decision or validation gates] |

#### Review response

Response: [Accept / Accept with recorded changes / Needs discussion]

Reviewer and date: [Name and date]

Changes or questions: [Reference workflow steps and requirement IDs.]

Decision record: [Accountable approver and authoritative record; a filled response is not automatically an approved scope change.]

## Supporting documentation

| Reference | Purpose | Version or source |
| --- | --- | --- |
| [Scope baseline] | Product boundary | [Reference] |
| [Requirements authority] | Exact commitments | [Reference] |
| [Delivery plan] | Work packages and sequencing | [Reference] |
| [Decision and validation records] | Gate status and closure evidence | [Reference] |

## Out of scope

Keep excluded, deferred, and optional items separate. Optional items require explicit scope approval before they become delivery commitments.

| Requirement or capability | Disposition | Boundary or inclusion condition | Source |
| --- | --- | --- | --- |
| [ID or capability] | [Excluded / Deferred / Optional] | [Reason or explicit approval condition] | [Reference] |

## Final review response

Overall response: [Response]

Reviewer and date: [Name and date]

Outstanding changes: [Requirement IDs, owners, and authoritative decision references]

Approval record: [Record or Not yet approved]
