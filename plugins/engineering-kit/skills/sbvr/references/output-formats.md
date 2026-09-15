# SBVR Output Formats

This file defines the skill's optional house formats, not a format required by SBVR. Use them for new artifacts when the user chooses them or when a project already follows this profile. Otherwise preserve the project's existing SBVR notation and schema.

This file describes the YAML format. For the Markdown format, see
[Part 7 of the guide](guide.md#part-7-formatting-sbvr-specifications). See the
[streaming-service example](../examples/streaming-service-sbvr.md) for a full narrative artifact.

## When to Use Each Format

Use **narrative markdown** by default. Pick it whenever the user is going to read the spec themselves, share it with non-technical stakeholders, or include it in a written document.

Switch to **structured YAML** when the user explicitly says any of these:
- "machine-parseable", "machine-readable"
- "tool-friendly", "for tooling", "for automation"
- "structured", "as data", "as a model"
- "we want to validate this in CI", "we want to generate code from this"
- "a downstream system needs to consume it"

If the user is ambiguous, default to markdown and ask whether they want a YAML version too. You can produce both — they're not mutually exclusive.

## YAML Schema (Canonical)

The YAML format below is the canonical schema. Use it exactly. Do not invent your own structure — downstream tools depend on these field names.

```yaml
specification:
  title: "Library Lending System"
  version: "1.0"
  scope: "Member accounts, books, loans, and fines for the library system"

vocabulary:
  - id: term-member
    term: member
    definition: "a person registered with the library to borrow books"
    reference_scheme: "library card number identifies member"
    note: "Members are either adult members or junior members"
    general_concept: null  # set when this term specializes another

  - id: term-adult-member
    term: adult member
    definition: "a member who is 18 years of age or older"
    general_concept: term-member

  - id: term-loan-period-policy
    term: loan period policy
    definition: "a policy that specifies the loan duration for adult and junior members"
    note: "Current setting: adult members 14 days, junior members 21 days"
    is_policy: true   # mark policy noun concepts explicitly

fact_types:
  - id: ft-member-borrows-copy
    preferred: "member borrows book copy"
    alternative: "book copy is borrowed by member"
    references: [term-member, term-book-copy]
    quantification:
      - direction: "member to book copy"
        statement: "each member borrows zero or more book copies"
      - direction: "book copy to member"
        statement: "each book copy is borrowed by at most one member at a time"

rules:
  - id: D1
    type: definitional
    statement: "It is necessary that each junior member has exactly one guardian member"
    references: [term-junior-member, term-guardian-member]

  - id: D2
    type: definitional
    statement: "It is impossible that a copy status is other than available, on loan, or lost"
    references: [term-copy-status]

  - id: B1
    type: behavioral
    modality: obligation   # one of: obligation, prohibition, permission
    statement: "It is obligatory that the due date for each loan is calculated as the date borrowed plus the loan period specified by the loan period policy for the borrowing member's member type"
    references: [term-loan, term-date-borrowed, term-date-due, term-loan-period-policy]

  - id: B2
    type: behavioral
    modality: prohibition
    statement: "It is prohibited that any member has more active loans than the active loan limit specified by library policy for that member's type"
    references: [term-member, term-loan, term-active-loan-limit-policy]
```

## Required Fields

Every YAML output must include all of these fields. Missing fields will fail downstream parsing.

- **specification** (top-level): `title`, `version`, `scope`
- **vocabulary** (list): each entry needs `id`, `term`, `definition`. Add `reference_scheme`, `note`, `general_concept`, `is_policy` only when applicable.
- **fact_types** (list): each entry needs `id`, `preferred`, `references`, `quantification`. Add `alternative` when natural.
- **rules** (list): each entry needs `id`, `type`, `statement`, `references`. Behavioral rules also need `modality`.

## ID Conventions

- **Term IDs:** `term-` prefix, kebab-case from the term name. `term-junior-member`, `term-loan-period-policy`.
- **Fact type IDs:** `ft-` prefix, kebab-case summarizing the relationship. `ft-member-borrows-copy`.
- **Rule IDs:** Same as the markdown format. `D1`, `D2`, `B1`, `DR1`, `ST1`.

IDs must be unique across the file. Do not reuse a term ID for a fact type or vice versa.

## References Field

The `references` field on fact types and rules is the bridge that lets a downstream tool walk the graph. List every term ID and fact type ID the entry depends on. A tool can then validate that no rule references a term that isn't defined, build cross-reference reports, or generate test fixtures.

This is the main reason the YAML format exists. Without explicit references, the model is just a markdown document with extra ceremony.

## Policies in YAML

Policy noun concepts get the same `is_policy: true` flag as other terms. Rules reference them by ID just like any other term. Under this house profile's threshold convention, configurable numeric settings belong in policy terms rather than rule statements.

## Optional: Multi-Vocabulary Layout

For large domains split across multiple vocabularies, use this top-level layout:

```yaml
specification:
  title: "Bank Operations"
  version: "1.0"
  scope: "Lending, deposits, and compliance operations"
  vocabularies:
    - lending
    - deposits
    - compliance

vocabulary:
  - id: term-loan
    term: loan
    vocabulary: lending
    ...

  - id: term-account
    term: account
    vocabulary: deposits
    ...
```

Each term, fact type, and rule gets a `vocabulary` field naming its home vocabulary. See [modularity.md](modularity.md) for when to split a domain into multiple vocabularies and how to handle terms shared across them.

## What NOT to Include in YAML Output

- **No manual term index.** The vocabulary list IS the index. A tool can sort it alphabetically by parsing the `term` field.
- **No "format_rationale" or meta-commentary.** Keep the file declarative. Explanations belong in human-facing docs, not the model.
- **No ad-hoc fields.** Every field above is part of the schema. Adding `attributes`, `cardinality`, `entities`, or other invented sections breaks downstream tools.
- **No hard-coded configurable settings in rule statements when using the house policy-reference convention.** Structural cardinalities and justified fixed values are separate modeling decisions.
