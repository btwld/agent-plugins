# Reference Implementation Notes

Use these notes only when shared written context will make a large or collaborative implementation
easier to verify. Delete every section that does not clarify the actual problem.

## Semantic contract

- Purpose:
- Inputs and outputs:
- Definitions and boundary conventions:
- Ordering or tie-breaking:
- Edge and failure behavior:
- Non-goals:

## Rule ownership

Record only behavior whose owner could otherwise become ambiguous.

| Rule | Authoritative owner | Enforcement sites, when distinct | Behavior tests |
|---|---|---|---|
| | | | |

## Boundaries and representations

List only boundaries where assumptions, guarantees, ownership, authority, failure behavior, or side
effects change. A conceptual step does not need its own code layer.

| Boundary or representation | What changes here | Why it remains separate |
|---|---|---|
| | | |

## Verification

- Golden and edge cases:
- Invariants or properties:
- Compatibility or migration evidence:
- Operational constraints, when relevant:
- Remaining uncertainty:

## Rejected complexity

Note an abstraction, representation, dependency, or extension point only when recording why it was
rejected will prevent the same unnecessary complexity from returning.
