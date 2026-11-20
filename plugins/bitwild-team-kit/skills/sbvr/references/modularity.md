# Multi-Vocabulary Modularity

> This is design guidance, not a fixed SBVR sizing rule. Split vocabularies when meaning, ownership, audience, or change boundaries justify it; preserve a coherent existing modular structure.

When a domain becomes difficult to navigate or govern as one specification, reviewers may struggle
to find what they need, term names may collide ("account" can mean something different in lending
and deposits), and small edits may ripple through the whole document. This reference covers how to
split a large domain into multiple vocabularies and keep them working together.

## When to Split

Default to **one vocabulary per spec**. Only split when you hit one of these:

- **Term collisions:** the same word means different things in different parts of the business. "Account" in lending vs deposits, "policy" in insurance vs IT security, "position" in HR vs trading. One vocabulary cannot define a term twice.
- **Reviewer fatigue:** the spec is too long for any one stakeholder to read end-to-end. Different teams own different sections and only care about their parts.
- **Independent change cycles:** different parts of the spec change on different schedules. Rules-of-the-road vocabulary is stable for years; promotions vocabulary churns weekly.
- **Genuine domain boundaries:** the business itself treats two areas as separate. Bank operations vs bank compliance. Game rules vs match analytics.

If none of these apply, stay with one vocabulary. Splitting prematurely creates more work than it saves.

## SBVR's Underlying Concepts

SBVR formalizes this with two concepts worth knowing:

- **Semantic community:** a group that shares a body of meanings — what concepts exist and how they relate. A bank is a semantic community.
- **Speech community:** a sub-group within a semantic community that shares a specific set of words for those meanings. The lending team and the compliance team are different speech communities of the same bank — they share the meaning of "borrower" but use different terminology around it.

In practice, each vocabulary corresponds roughly to one speech community. Two vocabularies can define different terms for the same underlying meaning, and a translation layer maps between them.

You don't need to use these terms in your spec. They just give you the right mental model: vocabularies are not arbitrary file boundaries, they reflect how the business actually carves up its language.

## How to Split

Split only when language, ownership, or lifecycle evidence shows a real boundary.

### Step 1: Identify the bounded contexts

If you've worked with Domain-Driven Design, this is exactly the bounded-context exercise. Walk through the domain and ask: where does the same word change meaning? Where do two teams talk past each other? Where does a process clearly hand off from one group to another?

A useful test: pick a term that appears everywhere ("customer", "order", "policy"). Ask the people closest to each part of the business what it means. If you get materially different answers, you have a context boundary.

### Step 2: Name the vocabularies

Give each vocabulary a single-word or short-phrase name that reflects the speech community, not the file structure. `lending`, `deposits`, `compliance` — not `vocab1`, `vocab2`. The names appear in references, in tool output, and in conversation.

### Step 3: Place each term in exactly one vocabulary

Every term lives in exactly one vocabulary, even if multiple vocabularies talk about it. The vocabulary that **defines** the term owns it. Other vocabularies **import** it.

A term that genuinely belongs to multiple contexts (rare) lives in a "shared" or "kernel" vocabulary that all the others import from.

### Step 4: Handle cross-vocabulary references

When a fact type or rule in vocabulary A needs to reference a term from vocabulary B, do not redefine the term. Reference the foreign term explicitly:

```yaml
fact_types:
  - id: ft-loan-secured-by-collateral
    vocabulary: lending
    preferred: "loan is secured by collateral asset"
    references:
      - term-loan          # local: lives in lending
      - deposits.term-collateral-asset   # foreign: lives in deposits
```

In narrative markdown, write the foreign reference inline:

> **Fact Type: loan is secured by collateral asset** *(references collateral asset from the deposits vocabulary)*

The `vocabulary.term-name` notation is the convention. Adopt it consistently.

### Step 5: Handle terminology conflicts

If two vocabularies use the same word for different meanings, do not rename either. Each vocabulary uses its native term and the cross-vocabulary reference is fully qualified:

- In `lending`: **account** = a credit account a borrower draws against
- In `deposits`: **account** = a deposit account holding customer funds

A rule that needs to talk about both must use `lending.account` and `deposits.account` explicitly. Inside `lending`, "account" alone refers to the lending account. Inside `deposits`, "account" alone refers to the deposit account. This is the same pattern as namespaces in code.

## Anti-Patterns

**Splitting by document section.** Don't put "vocabulary" in one file and "rules" in another and call that modularity. That's just cutting one document in half. Real modularity is along business-meaning boundaries.

**The "shared" vocabulary that grows without bound.** A small kernel vocabulary for genuinely cross-cutting terms (date, money, identifier patterns) is fine. A "shared" vocabulary that ends up holding most of the domain because nobody wanted to argue about ownership defeats the purpose.

**Forced harmonization.** If lending and deposits define "customer" differently, don't force-merge them into one definition. The differences exist for a reason. Keep both definitions and rely on cross-vocabulary references.

**Vocabularies that nobody owns.** Each vocabulary needs a specific person or team responsible for it. An orphan vocabulary will rot.

## When Modularity Is Not the Answer

Sometimes a spec is hard to navigate not because it's too large but because it's poorly organized. Before splitting:

- Try grouping terms by domain within a single vocabulary using H3/H4 headers.
- Try putting policies in their own subsection rather than scattered across the vocabulary.
- Try inlining terms that have no independent business meaning or useful reuse instead of keeping
  them as standalone concepts.

If those don't help and the spec is still unwieldy, then split. Modularity is overhead — make sure you're getting something for it.

## Quick Decision Tree

```
Is the same word used with different meanings in different parts of the business?
├── Yes → Split into vocabularies along those meaning boundaries
└── No
    └── Is the spec too large for any single reviewer to handle end-to-end?
        ├── Yes → Try better internal organization first; split only if that fails
        └── No → Keep one vocabulary
```
