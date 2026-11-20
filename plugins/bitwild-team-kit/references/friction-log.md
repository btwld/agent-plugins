# Friction log

A friction log is a record of user difficulties, supporting evidence, and follow-up
decisions. UX friction research gathers and assesses public evidence; research
synthesis can contribute findings from supplied studies. Either can populate the
same project log. The log is an output, not another skill or a mandatory PRD section.

## Review an existing log

Use the project's existing tracker or format when present. Preserve IDs and history;
do not create a second authoritative list. Check each entry against its linked
evidence, identify duplicates, stale claims and contrary accounts, and distinguish
reported difficulties from behavior actually observed or reproduced. If evidence
is unavailable, record that limit rather than inventing verification.

Assess relevance and credible user impact. Frequency counts require identifiable
independent sources; public complaints do not establish population prevalence.
Record unresolved differences in platform, version, audience, and circumstances.
Keep an existing owner's priorities unless the requested review calls for a change.

## Lightweight fields

For a new log, use these fields when relevant. Keep unknown values explicit; do not
invent owners, severity scores, dates, causes, or commitments to fill a row.

| Field | Meaning |
| --- | --- |
| ID | Stable finding ID, e.g. `FR-001`; preserve existing IDs |
| Context | Product, audience, workflow/task, platform and version if known |
| Finding and consequence | What was difficult and its reported or observed impact |
| Evidence | Source IDs/links, source dates, source type, and contrary accounts |
| Verification | Reported, observed, reproduced, or not verified; include supporting check evidence |
| Disposition | Needs investigation, accepted for planning, deferred, duplicate, or resolved; preserve the project's vocabulary |
| Owner and next check | Known owner and the bounded action that could reduce uncertainty |
| Links | Related finding, requirement, question, or decision IDs, when those records exist |

Dates of vendor fixes are not dates of verified resolution. Mark resolved only with
evidence satisfying the project's resolution criterion, recording what was checked
and when. Accepted for planning is a decision, not implementation proof. Preserve
duplicate entries as references to the retained finding instead of counting them as
additional independent reports.

## Connect to requirements

A finding can motivate a proposed requirement or open question; it is not itself
an approved requirement. When PRD work is requested, cite the finding's underlying
sources, create or reuse the relevant record in the product model, and link its ID
from the log. Keep question answers in the shared decision records, not duplicated
in a log cell. WBS work refers to that same requirement baseline.

This is a human-review convention, not an addition to `product.schema.json`.
Do not insert friction records into the current product JSON or claim that its
validator checks a log. Use the project's existing machine-readable tracker or
format when supplied; adding a dedicated log schema/parser is separate work.

Save project logs outside the plugin. Do not automatically synchronize trackers,
create tickets, start monitoring, or import a log into the product model.
