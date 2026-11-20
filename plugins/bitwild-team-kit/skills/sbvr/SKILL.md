---
name: sbvr
description: "Use when the user mentions SBVR or wants to create, review, audit, validate, or update business vocabulary and business rules in structured natural language. Trigger on formalizing requirements into vocabulary and rules, writing business rules, reviewing SBVR specs, structured natural language, fact types, definitional rules, behavioral rules, derivations, terms, or controlled vocabulary documents. Do not use for ordinary API validation schemas or generic grammar review unless SBVR-style business vocabulary is requested."
---

# SBVR

Create, explain, review, or update business vocabulary and rules using SBVR concepts while preserving the terminology, format, and governance conventions of the user's organization.

## Scope

Use this skill for:

- noun concepts, verb concepts, fact types, definitions, and business rules
- structural and operative rule wording, including necessity, obligation, prohibition, and permission
- controlled natural-language review and ambiguity detection
- updates to an existing SBVR or SBVR-inspired artifact
- the bundled Markdown/YAML authoring profile when the user or project has chosen it

Do not use it merely because a task contains validation rules. API schemas, database constraints, CEL, and ordinary prose editing need this skill only when the user wants an SBVR business vocabulary or rules model.

## Required outcome

Match the deliverable to the request:

- For authoring, produce the requested vocabulary, fact types, and rules at the requested level of formality.
- For review, report concrete semantic or representation problems with locations and suggested fixes.
- For updates, preserve the artifact's established conventions and explain material changes.
- For explanation, answer directly; do not force a full specification or validation report.

State assumptions only when they affect business meaning. Never invent a rule, threshold, role, or definition to make the artifact look complete.

## Core modeling principles

1. **Use the business's language.** Define the speech community or business area when scope is ambiguous. Keep implementation details out unless they are themselves business concepts or the user explicitly includes them.
2. **Build vocabulary and fact types together.** A noun concept should have a business meaning and normally participate in a fact type or rule. Capture verb concepts as first-class relationships rather than treating the vocabulary as a noun-only glossary.
3. **Separate meaning from presentation.** SBVR concepts do not require this skill's Markdown headings, YAML schema, certainty labels, rule IDs, or validator. Follow an existing project format first.
4. **Choose modality deliberately.** Distinguish structural necessities from operative obligations, prohibitions, and permissions. Use controlled wording when it improves precision, while respecting the user's selected SBVR notation or structured-English profile.
5. **Make quantification explicit when it matters.** Clarify cardinality and scope rather than silently assuming them. Numeric values can legitimately appear in rules; model a value as a separate policy concept only when it is genuinely configurable or centrally governed and that indirection helps the artifact.
6. **Preserve uncertainty.** Ask or flag a material ambiguity instead of fabricating an answer. Use the project's evidence or certainty scheme if one exists; the four-label scheme in the bundled discovery profile is optional.
7. **Validate semantics separately from syntax.** Mechanical checks can find format and wording issues, but they cannot establish that a rule is true, practicable, owned by the business, or complete.

## Authoring workflow

Scale this workflow to the source and requested deliverable.

1. Establish the business area, audience, source authority, and requested format.
2. Extract candidate business statements, then identify the noun concepts, verb concepts, constraints, policies, and open questions they imply.
3. For noisy discovery, migration, or integration material, use [references/extraction.md](references/extraction.md) to distinguish business concepts from project and implementation artifacts. A clean, small request does not need a formal classification ledger.
4. Define the concepts needed by the requested rules. Genus-and-differentia definitions, synonyms, examples, and reference schemes are useful where they clarify meaning; do not add empty metadata.
5. State relevant fact types and quantification. Consider both directions of a relationship, but record only constraints supported by the source or confirmed assumptions.
6. Write the rules with the appropriate modality and scope. Preserve user-supplied values unless there is evidence they are configurable policies or the user requests the bundled policy-reference convention.
7. Surface unresolved business questions that block correctness. Do not manufacture completeness.
8. Format the result using the user's existing conventions. If none exist and a durable artifact is requested, choose a simple readable structure or the optional bundled profile below.
9. Review the result for undefined concepts, ambiguity, unsupported assumptions, inconsistent modality, and contradictions.

For status-heavy domains, [references/lifecycle-modeling.md](references/lifecycle-modeling.md) offers one useful status/fact-type pattern. Treat it as a modeling heuristic, not a universal requirement: existing vocabularies or temporal models may represent change differently.

For large domains, consult [references/modularity.md](references/modularity.md) only when ownership, conflicting meanings, or change boundaries make multiple vocabularies useful.

## Reviewing an existing artifact

1. Identify the artifact's intended SBVR notation, local profile, scope, and audience before judging formatting.
2. Trace each rule to defined concepts and fact types where the artifact's modeling style expects them.
3. Check modality, quantification, ambiguity, contradictions, and whether the rule expresses the stakeholder's intended meaning.
4. Distinguish business-language leakage from legitimate technical-domain vocabulary. Terms such as API or database are not automatically invalid if the business community actually governs them.
5. Treat numeric thresholds as a problem only when they contradict the selected profile, duplicate a governed policy value, or are unsupported—not simply because they contain digits.
6. Separate semantic findings from local-format or tool findings. Prioritize issues that change meaning or prevent use.
7. Use [references/checklist.md](references/checklist.md) only for artifacts that adopt the bundled profile, or adapt its checks explicitly to the artifact rather than presenting every item as an SBVR mandate.

## Updating an artifact

1. Identify the requested semantic change and its affected concepts, fact types, rules, and references.
2. Preserve existing identifiers and formatting unless the change or user requires renumbering.
3. Apply the smallest coherent change, then check affected references and rules for contradictions.
4. Use the bundled renumberer only for compatible narrative Markdown and preview it with `--dry-run`.
5. Report the material changes and any unresolved business questions.

## Optional bundled authoring profile

This skill includes an opinionated house profile for teams that want a consistent, mechanically checkable artifact. It is **not the definition of SBVR compliance**. Use it when the user asks for this profile, the repository already uses it, or a new standalone artifact would benefit from its conventions.

The profile provides:

- narrative Markdown and a structured YAML schema
- vocabulary, fact-type, and rule sections with addressable identifiers
- controlled rule openings such as `It is necessary that` and `It is obligatory that`
- an optional `Confirmed / Confirmed shape / Candidate / Open` discovery scale
- an optional convention that moves configurable numeric settings into policy noun concepts
- a validator and a Markdown rule renumberer

Read [references/output-formats.md](references/output-formats.md) before producing the profile's YAML. The worked example at [examples/streaming-service-sbvr.md](examples/streaming-service-sbvr.md) demonstrates this profile, not the only valid SBVR representation.

### Profile tooling

Run bundled scripts from the selected skill directory. Inspect help before first use in an unfamiliar environment.

```bash
python3 "/absolute/path/to/selected/sbvr/scripts/validate.py" path/to/spec.md
python3 "/absolute/path/to/selected/sbvr/scripts/validate.py" path/to/spec.yaml
python3 "/absolute/path/to/selected/sbvr/scripts/validate.py" path/to/spec.md --json
python3 "/absolute/path/to/selected/sbvr/scripts/renumber.py" --dry-run path/to/spec.md
```

YAML validation requires PyYAML in the selected Python environment. Ask before installing it.

The validator checks conformance to this profile: expected sections and captions, its rule-wording and numbering conventions, its policy-threshold convention, selected jargon heuristics, and cross-references. It does not prove general SBVR compliance or business correctness. Treat its findings as evidence to review, not automatic truth; `--strict` changes exit behavior, not semantic certainty.

## Supporting files

- [references/guide.md](references/guide.md) — detailed SBVR concepts plus the bundled profile's examples and conventions; distinguish its modeling guidance from its house-format rules.
- [references/extraction.md](references/extraction.md) — optional discovery workflow for noisy source material.
- [references/lifecycle-modeling.md](references/lifecycle-modeling.md) — optional status-modeling heuristic.
- [references/modularity.md](references/modularity.md) — vocabulary-splitting guidance for genuinely large or independently governed domains.
- [references/checklist.md](references/checklist.md) — bundled-profile checklist; adapt rather than applying blindly.
- [references/output-formats.md](references/output-formats.md) — bundled Markdown/YAML representation.
- [examples/streaming-service-sbvr.md](examples/streaming-service-sbvr.md) — a comprehensive example of the bundled profile.

## Final check

- Does the output answer the requested task without forcing the bundled profile?
- Are important concepts and fact types defined consistently?
- Are modality, quantification, and scope clear enough for the artifact's purpose?
- Are values and assumptions supported by the source or visibly marked?
- Are profile-specific findings labeled as such?
- Have mechanical results been kept separate from business-semantic judgment?
