---
name: research-synthesis
description: "Use when turning real interview notes, usability observations, survey responses, or customer feedback into evidence-backed themes and product decisions. Use ux-friction-research to discover public reports; study planning is a separate task; synthetic interviews do not establish real-user findings."
---

<!-- Adapted from anthropics/knowledge-work-plugins by Leo Farias. See ../../SOURCES.md for source attribution and license. -->

# Research Synthesis

Turn supplied research into traceable findings, meaningful uncertainty, and an actionable next decision.

## Establish the evidence

Identify the research question and decision from the request. Inspect supplied evidence before asking for more. Record methods, dates, sampling, and participant or source identifiers when available. Do not invent a researcher, sample size, or study history.

Distinguish people from records: a support ticket and interview from the same person do not establish two independent participants. Keep unresolved duplicates visible. Separate synthetic personas and generated examples from empirical evidence throughout the report.

## Develop findings

1. Extract observations, exact quotes, reported preferences, and observed behavior with source references.
2. Group related observations into themes relevant to the question. Check the themes against contrary evidence and outliers.
3. Count unique participants only when identities and denominators support it. Counts describe this sample; they do not estimate population prevalence without a suitable sampling basis.
4. Explain the interpretation and its limits. Keep observation, inference, and recommendation distinguishable.
5. Compare qualitative and quantitative evidence while checking population, time window, definitions, and instrumentation. Correlation or an uncontrolled before/after change does not establish cause.

Use segments only when the data support a meaningful behavioral distinction. Do not manufacture personas, opportunity sizes, impact scores, or engineering estimates to complete a template.

## Recommend

Tie the next action to specific findings and the decision's uncertainty. Consider severity as well as frequency: one credible access blocker may deserve attention before a common inconvenience. Where evidence is insufficient, recommend a bounded check or experiment rather than asserting a product outcome.

## Deliver

Fit the requested length and format. Usually include the decision, study scope, prioritized findings with evidence, contradictions, limitations, and next action. Include only supported themes. Use exact quotations sparingly and never put a paraphrase in quotation marks.

Work from supplied files or available authorized research and analytics tools. Extra connectors, another skill, and publication are not prerequisites for producing the synthesis.

If the requested output includes a friction log, use the shared
[friction-log convention](../../references/friction-log.md). Link findings back to
the actual research; do not turn every theme into a defect or approved requirement.
