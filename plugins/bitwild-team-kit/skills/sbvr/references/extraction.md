# Candidate Extraction, Classification, and Filtering

Load this optional discovery profile when creating an SBVR artifact from noisy discovery notes, a replacement-system project, or integration-heavy source material—anywhere the source mixes real business vocabulary with project, implementation, and migration language. The classification taxonomy and certainty labels below are local workflow conventions, not SBVR-mandated categories. Preserve an existing project scheme when one exists.

## Why a two-pass extraction

If you extract nouns first, every important-looking noun in the source can become a term before it has earned business meaning. Discovery material for a new or replacement system is dense with project-scope terms, incumbent-system names, migration steps, screens, and APIs. Noun-first extraction promotes those into formal vocabulary, and the result drifts into a requirements/project glossary instead of an SBVR.

So extract statements first, derive concepts from the statements, classify every candidate, then filter. Define only what survives.

## Pass 1: Extract candidate business statements

Capture statements, not terms. Scan the source for anything that describes:

- business things that exist
- relationships between business things
- obligations, permissions, prohibitions, or necessities
- status changes or lifecycle transitions
- calculations, allocations, reviews, or approvals
- configurable policies, thresholds, rates, or periods
- open questions that block confident rule writing

Example candidate statements:

- A subscriber may hold a subscription to a plan.
- A Premium subscription may allow more concurrent streams than a Basic subscription.
- A licensor statement includes the revenue earned from watch activity in a period.
- A payment may settle one or more invoices.

## Pass 2: Identify concepts from statements

From each statement, pull noun concepts and verb concepts *together*. A noun becomes vocabulary only when it participates in business meaning, fact types, policies, or rules — never define a noun in isolation just because it appears.

Statement: *A subscriber may hold a subscription to a plan.*

- Candidate noun concepts: subscriber, subscription, plan
- Candidate verb concept / fact type: subscriber holds subscription
- Possible behavioral rule: It is permitted that a subscriber holds a subscription to a plan

## Classify every candidate

Before writing any definition, label each candidate as exactly one of these:

| Class | What it is | Where it goes |
| --- | --- | --- |
| noun concept | a business thing | vocabulary (if it passes the test below) |
| verb concept / fact type | a relationship between business things | fact types |
| definitional rule | a necessity or impossibility | rules |
| behavioral rule | an obligation, prohibition, or permission | rules |
| business policy | a real, business-owned configurable policy | policy noun concept |
| source / evidence item | an incumbent system, document, or data source | traceability / source notes |
| implementation artifact | API, database, screen, field, encoding | excluded (implementation) |
| project / migration artifact | migration step, cutover, phase, replacement-system scope | excluded (project) |
| open / deferred topic | unresolved; blocks confident rules | open questions |
| exclude | none of the above; no business meaning | dropped |

Use the full classification when discovery-heavy or replacement-system material would otherwise turn into a project glossary. For a clean source, a lighter keep/exclude/open pass may be enough.

Two structural decisions show up constantly during classification and are easy to get wrong:

- **A candidate that names a state** (Sold, Active, Available, Paid, Closed) is almost always a **status value**, not a standalone noun concept or a subtype. Model the entity once and give it a status — see [lifecycle-modeling.md](lifecycle-modeling.md). The tell is words like status, state, stage, phase, pending, active, closed, locked.
- **A candidate that looks like a kind of an entity** (a Premium subscription vs a subscription, a Basic plan vs a plan) may be a permanent subtype OR a changeable attribute/role. Apply the subtype-vs-role test in `guide.md` Part 6.5 before defining it as a subtype: if an instance can stop being that kind during its life — a subscriber upgrades from Basic to Premium — it is a role/attribute or a status, not a subtype.

## The belongs-in-SBVR test

A candidate survives into the SBVR only if MOST of these are true:

- Business stakeholders would recognize the concept or rule as part of their domain language.
- The business can own, revise, enforce, or discontinue it.
- It carries business meaning, not just project meaning.
- It participates in fact types or rules.
- It is not merely a source system, screen, database, API, migration step, or implementation module.
- It is supported by confirmed evidence, or by clearly marked Confirmed-shape evidence — not a bare guess.

If a candidate fails the test, move it to traceability notes, source evidence, assumptions, or open questions — not the vocabulary.

## Evidence status and the question-vs-create rule

Discovery material is rarely uniformly certain. Some things are validated, some are confirmed in shape but fuzzy in detail, some are plausible guesses, and some are genuinely unknown. SBVR work goes wrong in two opposite ways: inventing a confident rule to cover an unknown, or silently dropping something real because a detail is missing. Both are avoidable if you tag certainty explicitly and follow one decision rule.

### Optional certainty scale

When the project has no evidence scheme and the bundled discovery profile is selected, these four labels provide one consistent option:

- **Confirmed** — directly supported by validated evidence (walkthrough, signed-off source). Safe to build on.
- **Confirmed shape** — the concept or relationship is confirmed, but a specific value, formula, role, or edge case is still unknown. Create the item; record the unknown as an open question.
- **Candidate** — a plausible shape that is not yet validated. Do not build on it until the business confirms it.
- **Open** — an unresolved question that blocks confident modeling. Not yet a term or rule; it lives in the Open Questions section, not in the vocabulary or rules.

(These supersede the older "Confirmed / Partial / Open" wording — "Partial" maps to "Confirmed shape," and "Candidate" is the new low-confidence-but-plausible tier.)

### The decision rule: question or create?

When the evidence is incomplete, decide deliberately rather than defaulting:

- **Concept/relationship confirmed, only a detail missing** → CREATE the term, fact type, or rule at **Confirmed shape**, and record the missing detail as an Open Question. Example: the business confirms a per-stream licensing fee accrues to a licensor, but the rate is unknown — create the `licensing fee` term and the obligation rule at Confirmed shape, and open a question for the rate. Do not invent the rate.
- **Existence itself unconfirmed** → do NOT write a rule. Record an **Open Question**. Add the noun as a **Candidate** term only if the noun clearly exists in the business; otherwise leave it out entirely. Example: "is there a prorated first invoice?" is unconfirmed — open a question, write no rule.
- **Never fabricate** a value, formula, threshold, role, or rule to fill a gap. An explicit Open Question is worth more than a confident-looking wrong rule, because a wrong rule reads as settled and gets built.
- **Don't over-defer — the opposite failure.** "Never invent" should not bury supported information. A confirmed relationship may justify a draft or confirmed-shape rule when its modality and core meaning are known; if those are not known, retain the supported concept or fact type and raise the rule as an open question instead of forcing a stub.

State how sure you are, in the item's own words — a one-line Note that says what IS known and what is not is far more useful than a bare "Open."

### Open Questions vs Deferred Rule Areas

These are different and should be separate sections:

- **Deferred Rule Areas** — topics deliberately OUT of scope for this spec (other modules, migration, integrations). You are choosing not to model them now.
- **Open Questions** — topics IN scope but UNCONFIRMED. You would model them if you could, but the evidence does not yet allow it. Each entry names the question, what is currently known and its certainty, what it blocks (which term or rule is stuck at Confirmed shape or Candidate), and any Candidate item created pending the answer.

### Open Questions are iterative — never assume the list is complete

A first pass will not surface every question. The Open Questions list is a living, non-exhaustive record, and it is expected to grow: as the business answers earlier questions, the answers routinely expose new ones, and as you revisit the source you will spot gaps you missed. Treat it that way.

Two consequences for how you work:

- **The absence of a question is not evidence of certainty.** When you are unsure whether something is settled, add a question rather than assume it is settled. Silence must never stand in for confirmation.
- **Never make an assumption to fill a gap** — not about a value, a rule, a role, a cardinality, or even about whether you have found all the questions. If a first pass leaves you unsure how complete the picture is, say so explicitly (a note that the Open Questions list is preliminary) rather than presenting it as final. The skill's job is to make uncertainty visible, never to paper over it with a plausible-looking guess.

### Write Open Questions client-ready — they are the next discovery agenda

The Open Questions are not an internal annotation; they are the deliverable you hand to the business to drive the next discovery conversation. Phrase each one so a stakeholder can answer it directly:

- **No SBVR jargon** — ask in the business's own words, not "what is the cardinality of fact type X."
- **Lead with what is already known and confirmed**, then state exactly what is unknown and why it matters. Example: *"We know a subscription enters a grace period when a payment fails. We do not yet know the grace-period length or how many retries occur before cancellation. Until this is confirmed, we cannot write the dunning and cancellation-timing rules."*
- **Say what each answer unlocks** — name the term or rule currently stuck at Confirmed shape or Candidate that the answer would let you finalize.
- **Group by likely owner** (finance, operations, legal) when the list is long, so it routes itself to the right people.

This turns the list from a record of uncertainty into an actionable agenda: answer these, and the model advances. Then the loop repeats — answers confirm some items, promote them from Confirmed shape to Confirmed, and usually surface new questions.

## Worked filtering examples

| Candidate | Classification | Decision | Reason |
| --- | --- | --- | --- |
| subscriber | noun concept | Keep | Business actor in subscriptions, billing, and entitlement. |
| subscription | noun concept | Keep | Business object carrying status, plan, and billing. |
| licensor statement | noun concept | Keep | Business artifact carrying revenue-share owed to a licensor. |
| Premium | status / role value | Model as a plan tier value, not a standalone noun | A changeable attribute of a subscription, not its own entity (a subscriber can upgrade/downgrade). |
| (incumbent billing system) | source / evidence item | Exclude from core vocabulary | A system, not a business concept, unless a rule directly depends on it. |
| recommendation engine | project-scope term | Exclude | Out of the in-scope business slice; not business vocabulary here. |
| regional licensing edge cases | open / deferred topic | Defer unless rules are confirmed | Too broad until jurisdiction-specific behavior is confirmed. |
| migration / cutover | project artifact | Exclude | Belongs in migration planning, not business vocabulary. |
| DRM license token / API / screen | implementation artifact | Exclude | Technical implementation language, not SBVR business semantics. |

A source-system or integration name earns a place in the vocabulary only when a business rule genuinely depends on it (for example, a rule that constrains what may be sent to a named system of record) — and even then, prefer modeling the business concept the system stands for over the system label itself.

## Subtraction pass

Before formatting the final document, do one removal pass. Delete from the vocabulary and rules:

- project-scope terms
- source / incumbent-system names
- implementation terms
- migration / cutover terms
- unresolved assumptions presented as rules
- generic nouns with no confirmed business behavior

This is the safety net for anything that slipped past the belongs-in-SBVR test. Leakage is much easier to spot once the whole spec is in front of you.

## Scale the rigor to the source material

A clean, well-specified domain — say, a library loan process with clear borrower, item, loan, due date, renewal, fine, and hold rules — does not need heavy filtering. Run the passes lightly and do not over-filter legitimate business concepts; the goal is to catch drift, not to strip out real vocabulary.

The full extract/classify/filter machinery earns its cost when the source is discovery-heavy, describes a replacement for an incumbent system, or is thick with integration plumbing (payment processors, CRMs, ERPs, sync jobs, webhooks). There, keep the business concepts and the rules that genuinely depend on them, and move the plumbing out of the SBVR. Match the effort to the actual risk of project-glossary drift.
