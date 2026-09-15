# Work breakdown review

[Project name] [Release or scope]

Review what will be delivered, in what order, and which decisions and evidence are needed before acceptance. Dates are planning targets unless an accountable authority has explicitly approved a commitment.

## Review control

| Field | Value |
| --- | --- |
| Project and release | [Project and release] |
| Prepared and version | [Date and version] |
| Planning authority | [Source and baseline] |
| Owner and reviewers | [Names or Unassigned] |
| Planning status | [Proposed / Approved with decision reference] |
| Review return | [Date and recipient] |

## How to mark this review

Record acceptance, requested changes, or questions against package and requirement IDs. Distinguish a planning target from a commitment and a decision from proof that its acceptance condition passes.

## Decisions and evidence owners

| Gate | Decision or evidence needed | Owner | Needed before | Closure record |
| --- | --- | --- | --- | --- |
| [Gate ID] | [Atomic uncertainty or required proof] | [Owner or Unassigned] | [Package or milestone] | [Decision reference or validation result] |

## Dependency loaded roadmap

[Insert a roadmap generated from the sequencing table. Show review, decision closure, agreed examples or contracts, build, and verification as distinct stages where applicable. Display dependencies and release acceptance gates. Use the project's actual releases, not the source project's dates or staffing assumptions.]

| Package | Review and decide | Agree example or contract | Build | Verify | Predecessor and gate |
| --- | --- | --- | --- | --- | --- |
| [ID] | [Window] | [Window] | [Window] | [Window] | [IDs and exit criteria] |

## What ships and in what order

| ID | Work package | Window | Build outcome | Proof of completion |
| --- | --- | --- | --- | --- |
| [ID] | [Name] | [Planning window] | [Deliverable] | [Measurable evidence or acceptance condition] |

## Work breakdown at a glance

[Insert the project's WBS hierarchy using stable parent and child package IDs. Organize around outcomes, using the project's own scope. Candidate groups are program decisions, shared platform, product delivery streams, conversion and release, and explicit later or excluded scope. Use only the groups that fit the project.]

## Complete work package dictionary

Repeat this definition for every package, including explicit deferred, optional, and excluded scope buckets used in the coverage ledger.

### Package [ID] [Name]

Parent: [Parent ID]

Outcome and included work: [Bounded deliverable]

Excluded work: [Boundary and related package if applicable]

Owner: [Named accountable owner or Unassigned]

Dependencies: [Predecessor package IDs and gates]

Completion evidence: [Acceptance condition and evidence owner]

Release disposition: [Current release / Optional / Deferred / Excluded]

## Release acceptance controls

| Milestone | Planning target | Entry conditions | Acceptance evidence | Decision owner |
| --- | --- | --- | --- | --- |
| [ID and name] | [Date or relative week] | [Package and gate IDs] | [Evidence and criteria] | [Owner or Unassigned] |

## Explicit later optional and excluded scope

| Scope | Disposition | Inclusion or reconsideration condition | Source |
| --- | --- | --- | --- |
| [Requirement or capability] | [Deferred / Optional / Excluded] | [Approval or dependency] | [Reference] |

## Complete requirement coverage

Every controlled requirement has exactly one primary WBS assignment, including requirements placed into later, optional, or excluded scope buckets. Cross references may exist, but must not create duplicate primary ownership or imply inclusion in a release.

| Requirement | Title | Disposition | Recommended delivery | Primary WBS | Work package |
| --- | --- | --- | --- | --- | --- |
| [ID] | [Authoritative title] | [Canonical disposition] | [Release or scope bucket] | [ID] | [Dictionary name] |

Coverage summary: [Source-derived totals by disposition].

Coverage checks: [All source IDs represented once; no unknown IDs; packages defined; dispositions match source; totals reconcile. Record actual results, not assumed passes.]

## Review response

Response: [Accept / Accept with recorded changes / Needs discussion]

Reviewer and date: [Name and date]

Changes requested: [Package or requirement IDs and proposed changes]

Approval record: [Authoritative reference or Not yet approved]
