# SBVR Modeling and House-Profile Guide

> This reference combines SBVR modeling guidance with the skill's optional Markdown/YAML house profile. The formatting, numbering, certainty labels, policy-threshold convention, and validator rules are local conventions, not universal SBVR requirements. Apply them only when that profile is selected.

SBVR helps you write business rules that both humans and computers can understand. It's about being precise without being technical.

**Important:** SBVR is technology-agnostic. It defines business semantics independent of implementation. When this guide mentions databases, APIs, or code, those are conventional mappings, not mandated by SBVR itself.

## Contents

- [What SBVR is NOT](#what-sbvr-is-not)
- [How to Use This Guide](#how-to-use-this-guide)
- [Process Notes](#process-notes)
- [Standards Alignment Note](#standards-alignment-note)
- [Part 1: The Foundation - Building Blocks](#part-1-the-foundation---building-blocks)
- [Part 2: The Two Fundamental Kinds of Rules in SBVR](#part-2-the-two-fundamental-kinds-of-rules-in-sbvr)
- [Part 3: Decision Guide for Rule Types](#part-3-decision-guide-for-rule-types)
- [Part 4: House-Profile Examples](#part-4-house-profile-examples)
- [Part 5: Patterns and Anti-Patterns](#part-5-patterns-and-anti-patterns)
- [Part 6: Advanced Modeling Topics](#part-6-advanced-modeling-topics)
- [Part 7: Formatting SBVR Specifications](#part-7-formatting-sbvr-specifications)
- [Implementation Checklist](#implementation-checklist)
- [References and further reading](#references-and-further-reading)
- [Appendix A: Objectification Patterns](#appendix-a-objectification-patterns)

## What SBVR is NOT

SBVR focuses on business semantics rather than prescribing a technical implementation or document format. Technical concepts can still belong when the relevant business community uses and governs them; the test is their meaning in the chosen vocabulary, not whether they sound technical.

### Categories usually outside the core vocabulary

| Category | Usually route outside the core business vocabulary unless business meaning depends on it |
| --- | --- |
| Database design | field types, VARCHAR, UUID, foreign keys, indexes, table names |
| File specifications | 44.1kHz, 320kbps, MP3, WAV, JSON, file size limits |
| API details | endpoints, rate limits, HTTP methods, request/response schemas |
| Architecture | microservices, queues, caching, storage systems |
| Date/time formats and encoding | ISO 8601 strings, Unix timestamps, specific timezone encodings (UTC offsets, etc.) |
| UI elements | buttons, dropdowns, modals, screens, navigation |
| Project & program scope | migration, cutover, replacement-system scope, target operating model, project phases, rollout steps |
| Source & incumbent systems | named legacy/incumbent systems and their labels, unless a business rule directly depends on them |
| Integration plumbing | sync jobs, webhooks, named CRM/ERP/payment-processor systems, unless a business rule directly depends on them |

For discovery notes, replacement-system projects, or integration-heavy source material, project and implementation labels can look like vocabulary while carrying no relevant business meaning. Use the extract → classify → filter passes in [extraction.md](extraction.md) when that risk is material.

### Procedural Language to Avoid

SBVR is declarative. Avoid step-by-step workflows and "the system does X" constructions.

**Avoid:** "System calls API, then validates response, then stores data"

**Prefer:** "It is obligatory that each response is validated before storage"

### Generic "system" actors

Using "the system" as the subject can hide the responsible business role or turn a rule into a procedural requirement. Prefer the actual actor or a declarative outcome when that is the intended meaning. Keep a system as an actor when it is a defined concept in the speech community and the rule genuinely governs its behavior.

**Avoid:**

- It is obligatory that the system sends email notification to manager when employee submits report
- It is obligatory that the system validates document signature before accepting submission
- It is obligatory that the system retrieves reference data from external service

**Prefer:** (Rewrite as passive/declarative)

- It is obligatory that email notification is sent to manager when employee submits report
- It is obligatory that document signature is validated before submission is accepted
- It is obligatory that reference data is retrieved from external service when identifier is assigned

**Key question:** Does naming the actor clarify responsibility or business meaning? If not, focus on the required outcome.

### The Business Stakeholder Test

When tempted to add implementation detail, ask:

> "Would a business stakeholder need to know this to understand the rule?"

If no, it usually belongs outside the core vocabulary unless the chosen speech community governs
that concept as part of its business meaning.

---

## How to Use This Guide

- **New to SBVR?** Read Parts 1-2, try examples in Part 4
- **Writing specifications?** Use Part 3 (decision guide) and Part 5 (patterns)
- **Validating?** See Implementation Checklist at end

---

## Process Notes

> AI-Assisted Authoring: When using AI tools, review output for invented terms not in requirements. AI tends to add plausible-sounding content—verify every term against source documents.

> Diagrams: Visual diagrams can aid stakeholder validation but are not part of the SBVR specification itself. The text is authoritative; diagrams are supplementary.

---

## Standards Alignment Note

This guide draws on SBVR concepts and adds project-specific conventions for representation, quantification, reference schemes, discovery certainty, and policies. Consult the applicable OMG specification and the project's chosen notation when exact standards conformance matters.

---

## Part 1: The Foundation - Building Blocks

Build the vocabulary before writing rules that depend on its terms and fact types.

### Naming Conventions

For a new artifact using this profile, these conventions are useful defaults:
- **Use singular form** — "customer" not "customers"
- **Avoid abbreviations** — "identifier" not "ID" (abbreviations can be noted as synonyms)
- **Pick one term for synonyms** — choose "customer" or "client", not both
- **Use business language** — "customer identifier" not "customer_id"

### When to Define a Term

Define a term when doing so removes ambiguity or supports the model, for example when:
- It participates in important fact types or rules
- It has a unique identifier (reference scheme)
- It's a specialized concept (inherits from a parent)
- Multiple interpretations exist without a definition
- It represents a quantifiable state or status

Usually avoid separate entries for:
- Modifiers that are better represented as a fact, role, or status
- One-off measures that need no shared meaning or governance
- Implementation artifacts outside the selected speech community

### 1. Terms (Noun Concepts - Business Vocabulary)

**What it is:** The nouns of your business - people, things, concepts

**How to define them:** the term is a `####` heading; its definition is the prose directly under the heading; everything else is a bullet.

```
#### term name
[genus] that [differentia].

- General Concept: [parent concept, if specializing]   (optional)
- Reference Scheme: [identifier] identifies [term]   (for identified concepts)
```

Only include fields that apply. `General Concept` is for specialization hierarchies. `Reference Scheme` is for noun concepts individually identified in systems (customers, accounts, orders)—not pure values (temperature, discount rate). Constraints on a term (necessity/impossibility) live in the Rules section as definitional rules, not under the term entry.

**Example:**

```
#### customer
a person or organization that has an agreement with our company.

- Reference Scheme: customer identifier identifies customer
```

Its identifier constraints ("each customer has exactly one customer identifier") are written as definitional rules in Part 3.

**Specialized Concept Example:**

```
#### manager
an employee who supervises other employees.

- General Concept: employee
- Note: Inherits the employee identifier reference scheme.
```

**Enumerations (closed sets of values):**

In this house profile, express closed enumerations through **definitional rules** rather than a custom vocabulary caption:

```
#### role
a designation that determines user permissions.

- Reference Scheme: role name identifies role
```

The enumeration itself is a definitional rule (Part 3): "It is impossible that a role is other than admin, editor, or viewer." SBVR treats all constraints as rules, which keeps a single source of truth and enables formal validation. The rule IS the enumeration.

Each permissible value can optionally have its own term definition if it has unique behavior:

```
#### admin
a role that grants full system access.

- General Concept: role
```

The most common enumeration in business domains is a **status**. The same pattern applies — "It is impossible that a contract status is other than Sold, Pending, Active, or Terminated" — but a status also needs *transition* rules that say which state changes are allowed. Enumeration closes the values; transitions govern movement between them. See the full lifecycle pattern in [lifecycle-modeling.md](lifecycle-modeling.md) (and Part 6.4) whenever the domain has statuses, states, stages, or phases.

### Vocabulary Captions

SBVR defines **official** caption types for vocabulary entries. These are the standard captions from SBVR 1.5:

### Primary Captions (Most Commonly Used)

| Caption | Purpose | Required |
| --- | --- | --- |
| `Definition:` | Genus + differentia definition - the essential meaning | Yes |
| `General Concept:` | Parent concept for specialization hierarchies | When specializing |
| `Reference Scheme:` | How instances are identified/distinguished | For identified concepts |
| `Note:` | Annotations, clarifications, explanations | Optional |
| `Example:` | Illustrative instances of the concept | Optional |

### Secondary Captions (For Special Cases)

| Caption | Purpose | When to Use |
| --- | --- | --- |
| `Source:` | Citation of external documentation | When definition comes from external standard |
| `Synonym:` | Alternative designation for the same concept | When multiple terms exist |
| `Dictionary Basis:` | Labels a definition adapted from a dictionary | When borrowing from standard dictionaries |
| `See:` | Points to preferred representation | When primary representation is deprecated |
| `Synonymous Form:` | Alternate wording for verb concepts | For verb concept entries only |
| `Description:` | Extended explanation beyond the definition | When additional context helps understanding |
| `Descriptive Example:` | Sample material that typifies the concept | When examples need more detail than `Example:` |

> House-profile note on enumerations: use a definitional rule (`It is impossible that X is other than A, B, or C`) rather than adding a custom caption.

### Caption Usage Examples

**Note - for annotations:**

```
#### user
a person who accesses the system.

- Note: Inherits person reference scheme
- Note: Only active users can perform operations
```

**Source - for external standards:**

```
#### ISO country code
a two-letter code identifying a country.

- Source: ISO 3166-1 alpha-2

#### ISRC
a unique identifier for sound recordings.

- Source: ISO 3901
```

**Synonym - for alternative terms:**

```
#### track
a recorded musical performance.

- Synonym: song
- Synonym: recording
```

**See - for deprecated terms:**

```
#### buyer
- See: system administrator
- Note: buyer role merged into system administrator role
```

**Dictionary Basis - when adapting standard definitions:**

```
#### catalog
an organized collection of items with descriptive information.

- Dictionary Basis: Merriam-Webster
```

Use `Note:` for:
- Explaining inheritance ("Inherits X reference scheme")
- Clarifying constraints not captured elsewhere
- Providing business context
- Documenting why reverse quantification is omitted

> Glossary-First Reminder: Before writing terms, verify each noun comes from requirements and resolve uncertain terms with stakeholders before finalizing.

### 2. Verb Concepts & Fact Types (Relationships Between Noun Concepts)

**What it is:** How terms connect to each other - the sentences of your business

**How to write them:** the fact type signature is a `####` heading (no "Fact Type:" prefix); wordings are bullets; constraints group under one `Necessity:` label.

```
#### [term A] [verb] [term B]
- Preferred: [term A] [verb] [term B]
- Alternative: [term B] [passive verb] by [term A]

Necessity:
- [quantification from A to B]
- [quantification from B to A]
```

Necessity statements are rules ABOUT the fact type, not part of its definition. See Section 3 (Quantification) for how to express "how many" in each direction.

**Example:**

```
#### customer places order
- Preferred: customer places order
- Alternative: order is placed by customer

Necessity:
- each customer places zero or more orders
- each order is placed by exactly one customer
```

### 3. Quantification - How Many?

**Definition:** Quantification specifies HOW MANY instances can participate in a relationship. It answers "how many?" for each side of a fact type.

**Best practice:** Express quantification in every intended direction. Many fact
types warrant necessities in both directions so the constraints are explicit.

**SBVR terminology note on "necessity":**
The word "necessity" appears in two different contexts in SBVR:

1. **In fact types:** The "Necessity:" statements are *quantification rules* that constrain how many instances participate in relationships (e.g., "each customer places zero or more orders")
2. **In modal rules:** "It is necessary that…" expresses *alethic necessity* (definitional truth that cannot be otherwise)

Both are valid SBVR uses but serve different purposes. Context makes the meaning clear.

### Quantification in Natural Language (SBVR Normative Form)

SBVR expresses quantification in natural language. The table below shows common patterns:

| Natural Language (SBVR) | Meaning | UML/ORM Shorthand* | Example |
| --- | --- | --- | --- |
| **exactly one** | Must be 1, no more, no less | 1..1 | each order has exactly one customer |
| **at least one** | 1 or more (must have some) | 1..* | each customer has at least one name |
| **at most one** | 0 or 1 (optional single) | 0..1 | each person has at most one passport |
| **zero or more** | Any number including none | 0..* | each customer places zero or more orders |
| **at least n** | n or more | n..* | each team has at least n players |
| **at most n** | Up to n | 0..n | each customer has at most n credit cards |
| **at least n and at most m** | Range | n..m | each team has at least 5 and at most 11 players |

*Note: The range notation (1..*, 0..1, etc.) is ORM/UML shorthand, not SBVR standard. Use it for quick reference, but SBVR's normative form is natural language quantification.

### Complete Fact Type with Bidirectional Quantification

```
#### customer owns account
- Preferred: customer owns account
- Alternative: account is owned by customer

Necessity:
- each customer owns zero or more accounts
- each account is owned by exactly one customer

Note: The first Necessity shows customer→account (0..*). The second shows account→customer (1..1). These are rules ABOUT the fact type, constraining the relationship.
```

For each fact type, consider both directions of the relationship. Add quantification where the business imposes a real constraint. If one direction is unconstrained, do not invent a rule—either omit it or add a note that no constraint is specified in that direction.

**Single-Direction Fact Types:**

When the reverse direction has no business constraint, you may omit it:

```
#### employee has salary amount
Necessity:
- each employee has exactly one salary amount

Note: Reverse direction unconstrained (multiple employees may share same salary).
```

But when the reverse matters, always include it:

```
#### customer has email address
Necessity:
- each customer has at least one email address
- each email address belongs to at most one customer   (important uniqueness constraint)
```

### Modeling Value Attributes

SBVR models all attributes as **binary fact types** using the "has" pattern. There is no separate "attribute" construct.

**Pattern:**

```
#### [term] has [value attribute]
Necessity:
- each [term] has exactly one [value attribute]
```

**Example - Simple attributes:**

| Fact Type | Necessity |
| --- | --- |
| user has email address | each user has exactly one email address |
| song has release date | each song has at most one release date |

**When reverse quantification matters:**

```
#### user has email address
Necessity:
- each user has exactly one email address
- each email address belongs to at most one user
```

SBVR's fact-oriented approach treats ALL facts as relationships. What other modeling approaches call "attributes" are simply binary fact types with value terms.

### 4. Rules (Constraints on Facts)

**What it is:** The laws that govern your business - what must, should, or cannot happen.

Rules fall into two categories: **Definitional** (structural truth) and **Behavioral** (obligations/permissions). Part 2 covers these in detail with examples.

---

## Part 2: The Two Fundamental Kinds of Rules in SBVR

SBVR defines two rule categories based on modality: **Definitional (Alethic)** and **Behavioral (Deontic)**.

### Category 1: DEFINITIONAL RULES (Alethic Modality)

**Definition:** Rules that are true BY DEFINITION. They express logical necessity - things that cannot be otherwise. These define the structure of your business universe.

**Keywords:**

- `It is necessary that` (must always be true)
- `It is impossible that` (can never be true)

**Examples:**

- **D1:** It is necessary that each customer has exactly one customer identifier *(You literally cannot create a customer without an ID - by definition)*
- **D2:** It is necessary that each order contains at least one line item *(An order without line items isn't an order by definition in this vocabulary)*
- **D3:** It is impossible that a person has more than one birth date *(By definition, you're born once)*

### Derivation Rules (A Definitional Pattern)

**Definition:** A special type of definitional rule that specifies HOW something is calculated from other values. Derivations state what logically follows from other facts.

**When to use:** Only when the calculation isn't obvious and needs to be documented as part of the specification.

**Pattern:**

[computed term] = [formula using other terms]

The "=" notation is shorthand for "It is necessary that X equals Y."

**Keywords:**

- = (equals)
- sum of
- count of
- average of
- [term] of each [related term]

**Examples:**

- **DR1:** total price of order = sum of (price of each line item in order)
- **DR2:** account balance = sum of deposits - sum of withdrawals
- **DR3:** average order value = sum of (total price of each order) / count of orders

**When NOT to use:**

- **Use derivation:** "order total = sum of line item prices - discount amount"
- **Usually unnecessary:** "full name = first name + last name" (obvious)

---

### Category 2: BEHAVIORAL RULES (Deontic Modality)

**Definition:** Rules that express OBLIGATIONS and PERMISSIONS in the business. These can be violated but shouldn't be (obligations) or explicitly state what's allowed (permissions).

**Three Sub-types:**

### 2a. OBLIGATIONS

**Keyword:** `It is obligatory that`

**Examples:**

- **B1:** It is obligatory that each order is shipped within 2 business days *(Business policy - should happen but might be delayed)*
- **B2:** It is obligatory that each employee submits a timesheet by Friday *(Expected behavior but can be violated)*

### 2b. PROHIBITIONS

**Keyword:** `It is prohibited that`

**Formal note:** In deontic logic, "It is prohibited that X" is semantically equivalent to "It is obligatory that not X." SBVR supports both formulations. We use "prohibited" for readability.

**Examples:**

- **B3:** It is prohibited that an employee approves their own expense report *(System should prevent this)*
- **B4:** It is prohibited that a withdrawal exceeds the account balance *(Transaction should be blocked)*

### 2c. PERMISSIONS

**Keyword:** `It is permitted that`

**Examples:**

- **B5:** It is permitted that a manager overrides a discount limit *(Explicitly allowed exception)*
- **B6:** It is permitted that a customer returns an item within 30 days *(Stated allowance)*

**Note on Restricted Permissions:** In practice, SBVR often uses restricted permission, which pairs cleanly with prohibitions:

- **B7:** It is permitted that a manager overrides a discount limit only if the override amount is less than $500
- **B8:** It is permitted that a withdrawal exceeds the account balance only if the customer has overdraft protection

This "permitted only if…" form is more common in real specifications than unqualified permissions.

**House-profile convention:** Prefer "It is prohibited that …" over "It is obligatory that not …"
for negative constraints because it is easier to read. For conditional permissions, prefer the
"It is permitted that … only if …" pattern.

---

## Part 3: Decision Guide for Rule Types

Use the questions in order when the statement's rule category is unclear.

### Choosing Between Definitional and Behavioral (and Derivation)

Classify the statement by what it does to the business meaning, not by the wording of the source.

### Is it a calculation?

**YES → Derivation Rule (Definitional Pattern)**

- Use formula notation: X = [formula]
- Example: "total = sum of line items"
- These are definitional - they state what logically follows from other facts

**NO → Continue to next question**

### Can this ever be false or violated?

**NO → Definitional Rule**

- Use "It is necessary that" or "It is impossible that"
- This defines the structure of your business universe (by definition in this vocabulary)

**Choosing between "necessary" and "impossible":**

- **"It is necessary that"** → A constraint that must be enforced (positive framing)
    - "It is necessary that each customer has exactly one primary email"
- **"It is impossible that"** → A logical impossibility that cannot occur by definition (negative framing)
    - "It is impossible that a person has more than one birth date"

> Tip: Use "necessary" when stating what MUST exist. Use "impossible" when stating what CANNOT exist. Both are definitional - choose the framing that reads most naturally.

**YES → Behavioral Rule**

- Then ask: "What behavior do we want?"
    - Should happen → "It is obligatory that"
    - Must not happen → "It is prohibited that"
    - May happen → "It is permitted that" (consider "only if" restriction)

### Examples of Choosing

**Scenario:** "Every employee needs an employee ID"

- Calculation? No
- Can it be violated? No (system cannot create employee without ID)
- **Result:** Definitional - "It is necessary that each employee has exactly one employee identifier"

**Scenario:** "Order total is sum of line items"

- Calculation? Yes
- **Result:** Derivation (Definitional) - "total price of order = sum of (price of each line item in order)"

**Scenario:** "Employees should submit timesheets weekly"

- Calculation? No
- Can it be violated? Yes
- What behavior? Should happen
- **Result:** Behavioral/Obligation - "It is obligatory that each employee submits timesheet weekly"

**Scenario:** "Managers can override credit limits"

- Calculation? No
- Can it be violated? N/A (it's an allowance)
- What behavior? May happen
- **Result:** Behavioral/Permission - "It is permitted that a manager overrides a credit limit only if the override is justified in writing"

---

## Part 4: House-Profile Examples

Use these examples to inspect structure and references, not as mandatory domain content.

### Example 1: Employee Management System

A complete mini-spec in the standard heading format. Note how the two configurable thresholds (training window, transfer eligibility) live in policy Note fields, and the rules reference the policy terms instead of embedding the numbers.

```
# Employee Management - SBVR Specification

## Part 1: Vocabulary

### Core Concepts

#### employee
a person who works for the organization under a contract.

- Reference Scheme: employee identifier identifies employee

#### manager
an employee who supervises other employees.

- General Concept: employee
- Note: Inherits the employee identifier reference scheme.

#### department
an organizational unit that groups related business functions.

- Reference Scheme: department code identifies department

### Policy Concepts

#### onboarding training policy
a policy that specifies the training each new employee must complete and by when.

- Note: Current setting: core compliance training due within the first 30 days.

#### department transfer policy
a policy that specifies when an employee may change departments.

- Note: Current setting: eligible after 6 months in the current department.

## Part 2: Fact Types

### Organizational Relationships

#### employee works in department
- Preferred: employee works in department
- Alternative: department employs employee

Necessity:
- each employee works in exactly one department
- each department employs zero or more employees

#### employee reports to manager
- Preferred: employee reports to manager
- Alternative: manager supervises employee

Necessity:
- each employee reports to at most one manager
- each manager supervises zero or more employees

Note: manager is a role played by employee.

## Part 3: Rules

### Definitional Rules

**D1:** It is necessary that each employee has exactly one employee identifier.
**D2:** It is necessary that each department has exactly one department code.
**D3:** It is impossible that an employee reports to themself.

### Derivation Rules

**DR1:** department headcount = count of employees who work in the department.
**DR2:** average tenure = average of (current date minus hire date) across employees who work in the department.

### Behavioral Rules

**B1:** It is obligatory that each new employee completes the training required by the onboarding training policy.
**B2:** It is obligatory that each manager conducts performance reviews annually.
**B3:** It is prohibited that an employee approves their own timesheet.
**B4:** It is prohibited that a manager approves their own expense report.
**B5:** It is permitted that a manager supervises employees from different departments.
**B6:** It is permitted that an employee changes departments only if the department transfer policy permits the change.
```

---

## Part 5: Patterns and Anti-Patterns

Apply these checks only when the artifact uses the optional house profile.

### House-profile pattern: Policy reference

Under the optional house profile, a genuinely configurable threshold (a limit, period, rate,
count, percentage, or duration) can be represented by a **policy noun concept**, with the current
value in its Note field and the rule referring to that policy. Preserve supported source values,
structural cardinalities, and other project conventions when this abstraction is not selected.

**Why this matters:** Rules express stable business intent; policy values change all the time. If you bake "30 days" into a rule and the company switches to 45 days, every test, downstream system, and stakeholder review touching that rule must be re-examined. If the rule references a "loan period policy" instead, only the policy's Note field needs updating.

#### The Three-Part Discipline

1. **Define a policy noun concept** in the vocabulary, with current value in the Note field.
2. **Write the rule against the policy term**, not the number.
3. **Final scan:** look for duplicated configurable values in behavioral and definitional rules.
   Move them behind the policy term when the profile applies; do not flag structural cardinalities
   or supported source values solely because they contain digits.

#### Worked Examples

**Avoid (hard-coded value):**
- It is prohibited that a password has fewer than 8 characters

**Prefer (policy reference):**
- It is obligatory that each password meets the organization password policy

**Avoid:**
- It is prohibited that session duration exceeds 24 hours

**Prefer:**
- It is obligatory that each session terminates according to the session timeout policy

**Avoid (defines the policy and also embeds the number):**

```
#### loan period policy
a policy that specifies the loan duration for adult and junior members.

- Note: Current setting: adult members 14 days, junior members 21 days
```

- B1: It is obligatory that the due date for a loan created by an adult member is calculated as date borrowed plus 14 days

This *looks* correct because the policy term exists, but the rule still hard-codes "14 days". Anyone updating the policy will miss the rule.

**Prefer:**

- B1: It is obligatory that the due date for each loan is calculated as the date borrowed plus the loan period specified by the loan period policy for the borrowing member's member type

The rule never mentions a number. If the policy changes, only the Note field updates.

**Avoid (limits duplicated in rules):**
- B3: It is prohibited that an adult member has more than 10 active loans
- B4: It is prohibited that a junior member has more than 4 active loans

**Prefer:**
- B3: It is prohibited that any member has more active loans than the active loan limit specified by library policy for that member's type

(Note that one rule can replace two when the policy abstraction is correct.)

#### When numbers are appropriate

Under this convention, configurable policy settings belong in policy Note fields ("Current
setting: 14 days"), while structural cardinalities can remain in fact-type quantification ("each
group booking contains at least 5 and at most 50 reservations"). Preserve a number in a rule when
the source establishes it as intrinsic business meaning rather than a separately governed setting.

#### Where Policies Live

Policies are **noun concepts** defined in the vocabulary alongside other terms. Group them in a `### Policy Concepts` subsection if there are several.

```
#### organization password policy
a policy that specifies password requirements for system access.

- Note: Current requirements: minimum 8 characters, at least one uppercase letter, at least one number, no common dictionary words

#### session timeout policy
a policy that specifies when inactive sessions terminate.

- Note: Current setting: 30 minutes of inactivity

#### loan period policy
a policy that specifies how long a member may hold a borrowed copy.

- Note: Current setting: adult members 14 days, junior members 21 days
```

This approach keeps rules stable while values change. Update the Note field when thresholds change; the rules themselves don't need modification.

### Common Anti-Patterns to Avoid

Use these as review signals. Confirm that each one causes ambiguity, coupling, or loss of business
meaning in the target artifact before rewriting it.

### Anti-Pattern 1: Technical Leakage

**Avoid:**

```
#### customer_id
a varchar(36) UUID that uniquely identifies a customer in the database.
```

**Prefer:**

```
#### customer identifier
a code that uniquely identifies a customer.
```

**Borderline technical terms** are subtler. Words like "serialized," "instantiated," "deserialized," and "persisted" pass a developer's ear but fail the business stakeholder test. Prefer plain alternatives:

| Technical | Plain alternative |
| --- | --- |
| serialized representation | captured representation, recorded representation |
| instantiated | created |
| deserialized | restored, reconstructed |
| persisted | stored, saved |

### Anti-Pattern 1b: Circular Definitions

A term's definition must not use the term itself (directly or through synonyms).

**Avoid:**

```
#### external service
an external service that provides data enrichment.
```

**Prefer:**

```
#### external service
a third-party provider that supplies data enrichment.
```

---

**Avoid:**

```
#### reference data
a business concept that stores classification information.
```

**Prefer:**

```
#### reference data
a category or descriptor that classifies entities within the system.
```

### Anti-Pattern 2: Procedural Rules

See also "The System as Actor Anti-Pattern" in the introduction for detailed guidance on removing system-centric language.

**Avoid:**

When a customer places an order, the system:
1. Validates inventory
2. Calculates total
3. Sends confirmation email

**Prefer:**

- It is obligatory that each order is validated for inventory availability
- It is necessary that order total = sum of (price of each line item in order)
- It is obligatory that a confirmation is sent when an order is placed

### Anti-Pattern 3: Assumed Business Logic

**Avoid:**

```
#### premium customer
a customer whose annual purchases exceed $10,000.

- Note: Premium customers get free shipping
```

**Prefer:**

```
#### premium customer
a customer who qualifies for premium status according to organizational policy.

- Note: Qualification criteria defined by business policy
```

### Anti-Pattern 4: Implementation-Driven Relationships

**Avoid:**

```
#### customer has customer_address_id
- Note: Foreign key relationship to address table
```

**Prefer:**

```
#### customer resides at address
- Preferred: customer resides at address
- Alternative: address is residence of customer
```

### Anti-Pattern 5: Undefined Collectives

Don't use vague collective terms in rules without defining them.

**Avoid:**
- It is obligatory that each reference data entity has a unique identifier *(What is a "reference data entity"? Undefined and vague.)*

**Prefer (be explicit):**
- It is obligatory that each department code is unique
- It is obligatory that each category name is unique
- It is obligatory that each region identifier is unique

Or define the collective properly:

```
#### reference data
a classification concept that is one of: department, category, region, status.
```

### Anti-Pattern 6: Imprecise Temporal Language

Avoid vague time expressions in rules.

**Avoid:**
- It is obligatory that notifications are sent soon
- It is obligatory that updates happen when possible
- It is obligatory that response is provided in a timely manner

**Prefer:**
- It is obligatory that notification is sent within 24 hours
- It is obligatory that update occurs before end of business day
- It is obligatory that response is provided within 2 business days

---

### House-profile anti-pattern 7: Threshold leakage

A subtle but extremely common failure mode: the author correctly defines a policy noun concept, then writes the rule with the number anyway. The vocabulary looks fine, the rule looks fine in isolation, but the abstraction breaks the moment the policy value changes.

**Avoid:**

```
#### fine rate policy
a policy that specifies the per-day fine for overdue loans.

- Note: Current setting: $0.25 per day
```

- B5: It is obligatory that an overdue loan accrues a fine of $0.25 per day

**Prefer:**

- B5: It is obligatory that an overdue loan accrues a fine at the rate specified by the fine rate policy

**How to catch it during review:** when the policy-reference convention is selected, look for a
configurable value duplicated in a rule after a policy term has already been defined. A digit by
itself is not evidence of leakage; the house-profile pattern above explains the distinction.

---

### Anti-Pattern 8: Double Negatives in Rules

Double negatives ("impossible that...not," "necessary that...without...not") are hard to test and easy to misread. Rewrite as positive statements.

**Avoid:**
- It is impossible that validation depend on a contract that is not expressed by a snapshot included in that definition
- It is necessary that no workflow execute without a definition that has not been validated

**Prefer:**
- It is necessary that validation use only contracts expressed by snapshots included in that definition
- It is necessary that each workflow execute from a validated definition

---

## Part 6: Advanced Modeling Topics

These topics extend core SBVR patterns for complex scenarios. Most specifications won't need them—start with Parts 1-5 and add these as needed.

### 6.1 Explicit "for each" Quantification

Use explicit variable-like phrasing only when ordinary natural-language quantification leaves the
referent or scope ambiguous.

### When Rules Need "For Each" (Use When Ambiguous)

Most rules work fine with natural language:
**Clear:** "Each customer has exactly one customer ID"

Some rules are ambiguous without explicit quantification:
**Ambiguous:** "Withdrawal amount cannot exceed account balance" (Which withdrawal? Which account?)

**Pattern for explicit quantification:**

This style mirrors SBVR Structured English's variable binding to remove underspecified references. It's a readability device that makes implicit quantification explicit.

It is [modal operator] that for each [item] X of [container] Y, [rule about X and Y]

**Example (generic singular - preferred):**

- It is prohibited that the amount of a withdrawal that affects an account exceeds the balance of that account.

**Caution:** Avoid "It is prohibited that for each X…". This construction prohibits only the case where ALL instances satisfy the condition. Use generic singular ("a withdrawal that affects an account") or rephrase as "It is obligatory that for each X…, not…".

When using 'for each', prefer wording that reuses existing fact types and terms (e.g., 'withdrawal that affects an account') instead of introducing variable names like w and a.

**When to use:** Only when someone reading your rule asks "which one?"

**Don't overuse:** Start with natural language. Add "for each" only to fix ambiguity.

**More Examples:**

- It is obligatory that for each line item i of order o, the quantity of i is greater than zero
- It is necessary that for each employee e of department d, the salary of e is within the salary range of d

---

### 6.2 Time-Related Rules (Dynamic Constraints & Temporal Patterns)

In SBVR, time-related constraints are often discussed as **dynamic constraints**—rules about ordering and timing of states and occurrences.

### Temporal Keywords

**Ordering:**

- X precedes Y
- X follows Y
- X occurs before Y
- X occurs after Y

**Duration:**

- within [timespan]
- within [N] [time units] of [event]

**Examples:**

- **ST1:** It is obligatory that each order is shipped within 2 business days after order confirmation
- **ST2:** It is prohibited that shipment occurs before payment is received
- **ST3:** It is necessary that employee termination date follows employee hire date
- **ST4:** It is obligatory that password reset occurs within 24 hours of request

SBVR expresses temporal ordering via verb concept wordings (e.g., precedes, follows, within) and uses the OMG Date-Time Vocabulary (DTV) for standardized temporal concepts and patterns.

> We use simple temporal phrases such as 'within 2 business days', 'before', and 'after' and, when needed, map them to the OMG Date-Time Vocabulary (DTV). SBVR itself does not prescribe concrete date/time formats (for example, ISO 8601 strings or Unix timestamps); those are implementation details and stay outside this guide.

> Vocabulary reminder: Temporal terms used in rules (e.g., "business day", "session", "timeout period") should be defined as noun concepts in Part 1, not left as informal phrases. Define them once, then reuse consistently.

---

### 6.3 Objectification

When a relationship needs properties of its own (timestamps, costs, counts), you can treat it as a noun concept. See **Appendix A** for detailed patterns and examples.

Objectification makes instances of a verb concept available as a noun concept so the relationship
can carry properties or participate in other facts. Keep the underlying verb concept and its
objectification semantically linked; do not introduce a second, apparently independent relationship
with the same meaning. In a narrative artifact, choose clear primary wording and make explicit how
an `assignment` objectifies `service line is assigned to provider` rather than presenting them as
unrelated facts.

### 6.4 Status and Lifecycle (most common structural pattern)

When an entity moves through named states over its life (a contract Sold → Active, an invoice unpaid → paid → charged back, a statement open → closed → locked), a status fact type often makes the time-varying classification clearer than ordinary subtypes. Define `[entity] status` as a noun concept, close the allowed values if the set is known, and write transition rules when the business governs the transitions. This is a heuristic rather than a universal requirement; see [lifecycle-modeling.md](lifecycle-modeling.md).

### 6.5 Subtype vs Role

`General Concept` (subtype) and a role an entity plays capture different meanings. A stable kind is
a natural subtype candidate; a temporary, conditional, or relationship-dependent classification
is often clearer as a role, status, attribute, or temporal classification. Preserve an existing
model that already expresses the time semantics correctly.

One useful test is: *"Can an instance of the parent stop having this classification during its
lifetime?"* If yes, evaluate role, status, attribute, and temporal-classification models before
using an ordinary stable subtype.

For example, a changeable plan tier can be modeled with `subscription has plan`, while a partner's
temporary licensor role can follow from `partner holds content license`. A stable classification
may still be a subtype. Choose from the business meaning and the project's conceptual-model
semantics rather than applying the example mechanically. See 6.4 for a status-pattern option.

### 6.6 Typed Agreement and Document Specializations

Agreement-heavy domains often have kinds that share most structure but differ in a few rules. A parent noun concept with subtypes can work when the classification is stable and carries distinct meaning. A type-valued fact can be clearer when the classification changes over time or primarily selects a policy. Preserve the semantics of an existing conceptual model rather than converting it mechanically.

### 6.7 Partitive vs Associative Fact Types

Distinguish whole-part (partitive) relationships from peer (associative) ones — the choice changes quantification defaults and existence semantics. When one entity is structurally composed of another, use partitive phrasing ("invoice line is part of invoice", "watch event belongs to subscription"): the part typically has an "exactly one" necessity toward its whole and cannot exist without it. When two entities are associated but neither contains the other, use associative phrasing ("payment satisfies invoice", "subscription entitles access to title"). The test: *"Can the part-side entity exist independently of the whole-side?"* If no, the relationship is partitive.

### 6.8 Grandfathered and Temporally Scoped Rules

Some rules apply only to records created before or after a date (grandfathering), or values that
change by effective period. When a separately governed schedule owns those dates, scope the rule
with a temporal qualifier and keep the dated values in a **policy term** whose Note records the
historical and current values. Preserve an explicit cut-off in the rule when it is itself the fixed
business constraint or the project's established notation requires it.

### 6.9 Modal Scope and Conditional Rule Precision

Scope a rule to the right population. A universal rule applies to every instance ("It is obligatory that each statement collects only items not on a prior statement"); a scoped rule uses a relative clause to constrain a sub-population ("It is obligatory that a provider that holds an active contract in a new territory completes a walkthrough before service begins"). Prefer a single scoped rule with a relative clause over several near-duplicate rules, and prefer a precise relative clause over an over-broad universal that would wrongly constrain instances it should not. When the scope itself is conditional, "permitted … only if" (restricted permission) keeps the default closed.

---

## Part 7: Formatting SBVR Specifications

This section provides guidance for structuring SBVR specification documents. The goal is readability: a reader should quickly locate any term, relationship, or rule without scanning the entire document.

### 7.1 Formatting Approach

Use a **heading-based hierarchy** so every term and fact type is addressable, appears in the document outline, and can be cross-referenced. Headers organize; prose and bullets carry the content.

**Document structure:**
- H2 (`##`) for major parts (Vocabulary, Fact Types, Rules)
- H3 (`###`) for domain groups (User Concepts, Song Relationships)
- H4 (`####`) for each **term entry** and each **fact type entry**
- `---` horizontal rules to separate domain groups visually

**Entry formatting:**
- Each term and fact type is a `####` heading (the entry name is the heading text — no "Fact Type:" prefix needed; the heading already marks it)
- A term's **definition is the prose line directly under its heading**; secondary captions (Synonym, General Concept, Reference Scheme, Note) are bullets
- A fact type's wordings are `Preferred`/`Alternative` bullets; its constraints sit under a single `Necessity:` label as bullets
- Rules keep a **bold identifier** (`**D1:**`) followed by the rule text

Because `####` headings inside the Vocabulary and Fact Types sections are read as entries (by humans and by `validate.py`), do not use `####` for ad-hoc sub-grouping there — add another `###` domain group instead. Inside the Rules section, `####` may still group rule kinds (Obligations, Prohibitions) because rules are detected by their bold identifier, not by headings.

### 7.2 Document Organization

Organize specifications with these standard parts:

| Part | Content |
| --- | --- |
| **Part 1: Vocabulary** | All term definitions (noun concepts) — this section IS the term index |
| **Part 2: Fact Types** | All relationships (verb concepts) |
| **Part 3+: Rules** | Derivation, definitional, behavioral, temporal rules |

Do not produce a separate "Term Index" appendix. The `####` term headings in the vocabulary section already give readers an index (and a navigable outline). A duplicated list drifts out of sync the moment a term is added.

Within each part, organize by **domain** (Users, Songs, Audio, Reference Data). This groups related concepts for easier navigation.

### 7.3 Term Entries

**Format:** the term is a `####` heading; the definition is the prose under it; everything else is a bullet.

```
#### term name
[genus] that [differentia].

- General Concept: [parent term]   (for specialized concepts)
- Reference Scheme: [identifier] identifies [term]
- Note: [clarifications]
```

**Example from a real specification:**

```
#### user
a person who has authorized access to the music management system.

- Reference Scheme: user identifier identifies user

#### system administrator
a user who has full system access including user management and system configuration.

- General Concept: user
- Note: Inherits the user identifier reference scheme.
```

Constraints on a term (necessity/impossibility) live in the Rules section as definitional rules, not under the term entry — keep the vocabulary entry to the definition and its captions.

**Grouping guidance:**
- Use `###` domain groups to cluster related terms (### User Concepts, ### Reference Data)
- Specialized concepts follow their parent concept within the same group
- Use `---` separators between logical groups

### 7.4 Fact Type Entries

**Format:** the fact type signature is a `####` heading; wordings are bullets; constraints group under one `Necessity:` label.

```
#### [term A] [verb] [term B]
- Preferred: [term A] [verb] [term B]
- Alternative: [term B] [passive verb] [term A]

Necessity:
- each [term A] [quantification] [term B]
- each [term B] [quantification] [term A]
```

**Example:**

```
#### user has role
- Preferred: user has role
- Alternative: role is held by user

Necessity:
- each user has exactly one role
- each role is held by zero or more users
```

**For value attributes, use tables:**

| Fact Type | Necessity |
| --- | --- |
| user has email address | each user has exactly one email address; each email address belongs to at most one user |
| user has first name | each user has exactly one first name |
| user has last name | each user has exactly one last name |

### 7.5 Rule Entries

**Numbering prefixes:**

| Prefix | Rule Type |
| --- | --- |
| **DR** | Derivation Rules |
| **D** | Definitional Rules |
| **B** | Behavioral Rules |
| **ST** | Temporal/State Rules |

**Format — bold prefix followed by rule text:**

**B1:** It is obligatory that each user authenticates with valid credentials before accessing the system

**B2:** It is obligatory that each login attempt is recorded as an audit log entry

**Organization pattern for behavioral rules:**

Use H3 headers for rule domains, bold labels (or H4) for rule types, and `---` separators between domains:

### 3.1 Authentication

**Obligations:**

**B1:** It is obligatory that…

**B2:** It is obligatory that…

**Prohibitions:**

**B3:** It is prohibited that…

---

### 3.2 User Management

*(Pattern continues with the next domain…)*

### 7.6 Grouping Strategy Summary

| Content Type | Group By |
| --- | --- |
| **Terms** | Domain group (`###`); each term is its own `####` heading |
| **Fact Types** | Domain group (`###`); each fact type is its own `####` heading |
| **Value Attributes** | Entity, using tables for compactness |
| **Behavioral Rules** | Domain (`###`), then type (Obligations → Prohibitions → Permissions) |

> Key principle: Use markdown structure throughout. `####` headings mark each term and fact type entry, prose under a term heading is its definition, bullets list the remaining fields, and bold is reserved for rule identifiers (`**D1:**`). This creates scannable documents with a navigable outline.

---

## Implementation Checklist

See [checklist.md](checklist.md) for the full house-profile validation checklist. Use it when that profile applies.

---

### Rule Numbering Convention

Use category prefixes for traceability:

- **D1, D2, D3…** — Definitional rules
- **DR1, DR2…** — Derivation rules
- **B1, B2, B3…** — Behavioral rules
- **ST1, ST2…** — State transition rules (if applicable)

Keep numbering sequential within each category. When referencing rules in documentation or tests, use the full identifier (e.g., "Rule B12 requires…").

---

## References and further reading

Use primary standards for conformance questions and secondary material for interpretation.

### Official Standards

**OMG SBVR 1.5 Specification**

- https://www.omg.org/spec/SBVR/1.5/
- The authoritative source for all SBVR concepts, metamodel, and notation

### SBVR Speaks Series (Business Rules Community)

These articles by the SBVR standard authors provide essential guidance:

1. **"(4) The SBVR Vocabulary for Business Rules"**
    - https://www.brcommunity.com/articles.php?id=b280
    - Defines definitional rules, behavioral rules, and modal operators
2. **"(5) Notations for Business Rule Expression"**
    - https://www.brcommunity.com/articles.php?id=b286
    - SBVR Structured English notation styles and quantification keywords
3. **"(6) Concepts and Definitions in SBVR"**
    - https://www.brcommunity.com/articles.php?id=b288
    - General noun concepts, individual concepts, and proper definition structure
4. **"Changes in SBVR's Meaning and Representation Vocabulary"**
    - https://www.brcommunity.com/articles.php?id=b770
    - Evolution from 'object type'/'fact type' to 'noun concept'/'verb concept'

### Foundational Logic

**Deontic Logic (Stanford Encyclopedia of Philosophy)**

- https://plato.stanford.edu/entries/logic-deontic/
- Theoretical foundation for understanding obligation, permission, and prohibition

### Business Rules Community

- https://www.brcommunity.com/
- Ongoing articles, discussions, and best practices from SBVR practitioners

---

*This guide is aligned with SBVR 1.5 and uses project-specific notation and templates on top of it. Focus on the two fundamental rule categories (definitional and behavioral, with derivation as a definitional pattern), proper vocabulary structure using noun and verb concepts with readings, and quantification in natural language where the business imposes constraints.*

---

## Appendix A: Objectification Patterns

Objectification creates a noun concept from a verb concept—treating a relationship as if it were a thing.

**Example:** "person owns vehicle" (verb concept) → "ownership" (noun concept)

### When to Objectify

Ask: **"Does the relationship itself have properties or participate in other relationships?"**

- **Yes** → Create a noun concept (timestamp it, classify it, count it)
- **No** → Keep it as a simple fact type

### Pattern

```
#### [relationship-as-noun]
the relationship arising from [subject] [verb] [object].

- Objectified From: [original fact type]
```

### Example: Employment

**Before (simple fact type):**

```
#### employee works in department
Necessity:
- each employee works in exactly one department
- each department employs zero or more employees
```

**After objectification (when you need start dates and salary):**

```
#### employment
the relationship arising from an employee working in a department.

- Objectified From: employee works in department

#### employment started on date

#### employment ended on date

#### employment has salary amount
```

### Example: Order Fulfillment

**Without objectification:**

```
#### warehouse fulfills order
```
- Problem: Can't track WHEN fulfillment happened or cost

**With objectification:**

```
#### fulfillment
the relationship arising from a warehouse fulfilling an order.

- Objectified From: warehouse fulfills order

#### fulfillment occurred on date

#### fulfillment has cost

#### fulfillment was performed by employee
```

Use objectification whenever a relationship must behave like a thing in your vocabulary.
