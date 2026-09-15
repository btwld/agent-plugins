# SBVR Implementation Checklist

Use this checklist for artifacts that adopt the skill's optional Markdown/YAML house profile. Adapt it to other SBVR notations and project conventions; profile-specific formatting, numbering, certainty, and threshold items are not universal SBVR requirements.

## Vocabulary

- [ ] All terms referenced in fact types and rules are defined
- [ ] No circular definitions (term does not use itself)
- [ ] Specialized concepts note inheritance, not repeat parent's scheme
- [ ] Every term that requires instance-level identification has a reference scheme (skip for type-system or architectural specs where terms describe categories, not trackable instances)
- [ ] No reference schemes use technical identifiers (UUID, foreign key)
- [ ] Only captions supported by the selected profile are used (the bundled validator recognizes Definition, General Concept, Reference Scheme, Note, Example, Source, Synonym, and related profile captions)
- [ ] Enumerations expressed as definitional rules, not as captions
- [ ] Policies defined as noun concepts with current values in Note field

## Fact Types

- [ ] Both directions considered; real constraints explicitly stated
- [ ] Quantification uses natural language (exactly one, at least one, zero or more, etc.)
- [ ] Value attributes modeled as binary fact types using "has" pattern

## Rules

- [ ] Each rule expresses exactly one constraint (a qualifying clause that scopes the constraint, such as "independent of X," counts as part of the same constraint, not a separate one)
- [ ] Rule numbering is sequential with no gaps (D1, D2..., B1, B2..., DR1, DR2...)
- [ ] Rules are testable
- [ ] Definitional rules use only "necessary" or "impossible"
- [ ] Behavioral rules use only "obligatory", "prohibited", or "permitted"
- [ ] Derivation rules use formula notation (x = ...)

## Lifecycle, Status, and Classification

- [ ] Relevant entities with named states were considered, not only the obvious lifecycle (see `lifecycle-modeling.md`)
- [ ] Entities that adopt the status pattern use a single `[entity] status` fact type rather than transient status subtypes (see `lifecycle-modeling.md`)
- [ ] Where the business governs both a closed value set and transitions, the artifact includes both a definitional enumeration rule and the relevant behavioral transition rules
- [ ] Transient or role-like classifications were evaluated against status, temporal-classification, and role-granting relationship options; subtypes are retained where the business meaning or existing model makes them appropriate (see `guide.md` Part 6.5)
- [ ] Whole-part relationships use partitive phrasing; peer relationships use associative phrasing (`guide.md` Part 6.7)
- [ ] Time-varying or grandfathered rules keep dated values in a policy term, not in the rule (`guide.md` Part 6.8)

## Scope Validation

- [ ] Document scope is clear (what's IN vs OUT)
- [ ] No rules reference features outside defined scope
- [ ] External dependencies are explicitly listed

## Scope & Jurisdiction (Belongs-in-SBVR)

For discovery-heavy or replacement-system specs, confirm the vocabulary is business language, not a project glossary (see `extraction.md`):

- [ ] Every term carries business meaning, not just project meaning
- [ ] No source/incumbent-system names in vocabulary unless a rule directly depends on them
- [ ] Implementation artifacts (API, database, screen, field, encoding) are not promoted solely because they appear in project material; retain them when the chosen business community governs their meaning
- [ ] No migration/cutover/project-phase terms promoted to vocabulary
- [ ] Unresolved or too-broad topics are marked Open/Deferred, not promoted to terms or rules
- [ ] Each surviving term participates in at least one fact type or rule
- [ ] Excluded and deferred candidates are recorded in traceability/source notes, not silently dropped

## Anti-Pattern Check

- [ ] Generic "the system" actors are replaced when they obscure the responsible business role; retained when the system is a defined, meaningful actor
- [ ] No procedural language ("system does X then Y")
- [ ] **House-profile threshold check:** when the policy-reference convention is selected, configurable values live in a policy noun concept's Note field and rules reference the policy term; structural cardinalities and supported source values are not rejected merely because they contain digits
- [ ] Technical terminology is retained only when the chosen speech community uses and governs it; project implementation vocabulary does not leak into an otherwise business-facing model
- [ ] No undefined collectives (vague group terms)
- [ ] No imprecise temporal language ("soon", "when possible", "timely")
- [ ] No circular definitions
- [ ] No double negatives in rules ("impossible that...not" or "necessary that...not...without") — rewrite as positive statements using "only" or "exactly"
- [ ] No implementation-driven relationships (foreign keys, table names)

## Document Structure

- [ ] Part 1: Vocabulary (all term definitions)
- [ ] Part 2: Fact Types (all relationships)
- [ ] Part 3+: Rules (derivation, definitional, behavioral)
- [ ] Organized by domain within each part (`###` domain groups)
- [ ] Each term and fact type is a `####` heading; term definition is prose under the heading, captions are bullets, fact-type constraints group under one `Necessity:` label
- [ ] Rules keep a bold identifier (`**D1:**`) so they stay referenceable and renumberable
- [ ] **No manual term-index appendix** — the vocabulary section IS the index

## Rule Keywords Reference

| Rule Type | Keywords |
|-----------|----------|
| Definitional (must be true) | "It is necessary that" |
| Definitional (cannot be true) | "It is impossible that" |
| Obligation | "It is obligatory that" |
| Prohibition | "It is prohibited that" |
| Permission | "It is permitted that" |
| Restricted permission | "It is permitted that ... only if" |
| Derivation | "x = [formula]" |

## Quantification Reference

| Natural Language | Meaning |
|------------------|---------|
| exactly one | Must be 1 |
| at least one | 1 or more |
| at most one | 0 or 1 |
| zero or more | Any number including none |
| at least n | n or more |
| at most n | Up to n |

## Semantic Review (after mechanical validation)

The validator and the checks above catch structure, not meaning. Once they pass, review each rule by hand — this is where a stakeholder would catch a rule that is well-formed but wrong:

- [ ] Each rule is practicable (a person or the business could actually follow or enforce it)
- [ ] Each rule is business-owned (the business can revise or discontinue it)
- [ ] Each rule depends on a defined fact type
- [ ] When the optional certainty scale is used, each term and rule carries an agreed label such as Confirmed / Confirmed shape / Candidate / Open (see `extraction.md`)
- [ ] Under that scale, uncertain items follow the question-vs-create rule: create at Confirmed shape only when the concept is confirmed and only a detail is missing; otherwise raise an Open Question with no invented value, formula, or rule
- [ ] Under that scale, confirmed material is not silently over-deferred; only deliberately out-of-scope or genuinely open topics remain deferred
- [ ] Material in-scope unknowns appear in an **Open Questions** section (distinct from Deferred Rule Areas), each noting what is known, its certainty, and what it blocks
- [ ] The Open Questions list is treated as iterative/non-exhaustive (marked preliminary if completeness is uncertain); no assumptions were made to fill gaps — when unsure, a question was added rather than a guess
- [ ] Open Questions are phrased client-ready (no SBVR jargon; lead with what is known; say what each answer unlocks) so the list works as the next discovery agenda
- [ ] A business stakeholder would recognize the rule as theirs
- [ ] No source-system or implementation language is leaking into the rule
- [ ] Policy terms reflect real business policies, not values invented to avoid a hard-coded number

## From Rules to Tests

For each rule, verify you can create:
- **Positive example:** Scenario where rule is satisfied
- **Negative example:** Scenario where rule is violated (behavioral) or represents invalid state (definitional)
