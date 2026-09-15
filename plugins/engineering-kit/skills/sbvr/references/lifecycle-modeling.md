# Lifecycle and Status Modeling

This reference describes one useful status/fact-type pattern for entities that move through named states. It is a modeling heuristic, not an SBVR mandate; preserve an existing temporal, role, or classification model when it represents the business meaning correctly.

## The pattern

For many operational lifecycles, model the entity as one noun concept that carries a status rather than creating a subtype for every transient state.

1. Define the entity as a single noun concept (`subscription`).
2. Give it a status through a fact type: `subscription has subscription status` (each subscription has exactly one subscription status).
3. Define `[entity] status` as a noun concept, and close the allowed values with a definitional enumeration rule: "It is impossible that a subscription status is other than Trialing, Active, Past Due, Canceled, or Reactivated."
4. Write the allowed transitions as behavioral rules: "It is obligatory that a subscription reaches Active status only after a payment is settled" / "It is prohibited that a subscription returns to Trialing status once it has reached Active status."
5. Promote a specific status value to its own term (with `General Concept: [entity] status`) only if that value carries unique fact types or rules that apply to it alone.

## Why not subtypes

Modeling `trialing subscription` and `active subscription` as ordinary subtypes can obscure the time-varying nature of the classification and make transition rules awkward. A status fact type makes that change explicit. If the project's conceptual model gives classifications temporal semantics, or the classification is genuinely stable, preserve that model instead of converting it mechanically.

**Rule of thumb:** if an instance can move from one classification to another during its life,
status-value, temporal-classification, or role modeling is usually clearer than an ordinary stable
subtype. A permanent classification, such as a title that remains a movie or a series, may be a
subtype. Apply the subtype-vs-role test in `guide.md` Part 6.5 and preserve an existing model that
already represents time correctly.

## Worked example: subscription lifecycle

Vocabulary — one entity, one status concept:

```
#### subscription
an agreement under which a subscriber pays recurring fees for access to the service.

- Reference Scheme: subscription identifier identifies subscription

#### subscription status
the current lifecycle state of a subscription.

- Reference Scheme: subscription status name identifies subscription status
- Note: Allowed values are closed by a definitional rule; current values are Trialing, Active, Past Due, Canceled, Reactivated.
```

Fact type:

```
#### subscription has subscription status
- Preferred: subscription has subscription status
- Alternative: subscription status belongs to subscription

Necessity:
- each subscription has exactly one subscription status
```

Rules — one enumeration rule closes the set, behavioral rules govern transitions (IDs are illustrative; renumber to fit the spec):

```
**D-n:** It is impossible that a subscription status is other than Trialing, Active, Past Due, Canceled, or Reactivated.

**B-n:** It is obligatory that a subscription reaches Active status only after a payment for that subscription is settled.

**B-n:** It is prohibited that a subscription returns to Trialing status once it has reached Active status.
```

## Status drives other rules precisely

Once status is a first-class concept, other rules can reference it exactly instead of encoding the state into a subtype or leaving it implicit:

- "It is prohibited that an invoice is treated as paid before its invoice status is Settled."
- "It is obligatory that playback is permitted only for a subscription whose subscription status is Active or Trialing." (positive "only" phrasing avoids a prohibited-not double negative)
- "It is obligatory that a content license is hidden from the catalog once its content license status is Removed."

## Relationship to enumerations and transitions

When the business governs both a closed value set and allowed state changes, model the two concerns
with complementary rules:

- one **definitional enumeration rule** that closes the allowed values (`It is impossible that … is other than …`), and
- one or more **behavioral transition rules** that say which state changes are obligatory, prohibited, or permitted, and under what condition.

If both concerns are in scope, writing only the enumeration under-specifies the transitions, while
writing only transitions leaves the state set open-ended. Use both only when the source or confirmed
business model governs both.

## Find every status-bearing entity

When this pattern is selected, scan relevant entities rather than applying it only to the headline
lifecycle. State language such as *pending, settled, failed, refunded, charged back, trialing,
active, past due, canceled, acquired, available, expiring, removed, open, closed,* or *locked* can
reveal overlooked candidates. For each candidate, confirm whether the business actually needs a
status concept, a closed enumeration, transition rules, or some smaller subset. A payment that can
be "charged back" and a license that "expires" may have different modeling needs.

## Checklist

- [ ] Relevant entities with named states were considered, not only the headline lifecycle.
- [ ] Each entity that uses this pattern has a single `[entity] status` fact type rather than transient status subtypes.
- [ ] When the business defines a closed set, a definitional enumeration rule closes the allowed status values.
- [ ] When the business governs transitions, behavioral rules state the allowed, required, or prohibited changes and their conditions.
- [ ] Status values become their own terms only when they carry unique behavior.
- [ ] Other rules reference the status value by name rather than re-encoding the state.
