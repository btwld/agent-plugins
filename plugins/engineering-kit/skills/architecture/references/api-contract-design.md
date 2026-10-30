# API contract design

Use this guidance when a design direction is chosen and the consumer-facing contract needs to
become concrete. It applies to a new API or an approved redesign. If the unresolved question is
whether the existing solution should exist or be redesigned, use clean-sheet-review first only
when the user asked for that reconsideration.

## Start with the consumer

Establish the outcome, consumers, fixed constraints, and compatibility obligations. Inspect the
current signatures, a real caller, and relevant lifecycle or data flow when code exists. Keep
current facts separate from proposed behavior and unavailable evidence.

Show a minimal example of what a consumer would write, then a representative scenario that tests
the difficult part of the contract. Choose scenarios from the product; do not impose a CRUD app,
registry, universal primitive, or preferred framework pattern. Explain the concepts and trade-offs
in the consumer's language. Use framework conventions when they fit the constraints.

## Settle behavior and open decisions

Make inputs, outputs, invariants, ownership, errors, ordering, and lifecycle rules explicit where
relevant. Trace each public operation to a demonstrated need. Preserve useful boundaries; remove
concepts only when their responsibility disappears or is covered elsewhere.

Record agreed decisions with reasons and keep unresolved questions distinct. Use IDs or a small
table when cross-references help. Ask about the next consequential uncertainty rather than walking
every decision through a fixed ceremony. New evidence can reopen an agreed choice: explain the
impact and seek the needed decision instead of silently changing the contract or treating it as
permanently locked.

Keep one design record following repository conventions. Maintained API guides and ADRs belong in
the repository; working notes and plans use writing-plans' shared artifact convention unless a
location is specified. Link related records and preserve decision history. Do not commit records,
change accepted ADR status, or imply approval without authorization.

## Make the contract verifiable

Write requirements that an observable example or test can check. Cover representative consumers,
important errors and boundaries, and any migration obligations. Label example code as proposed
until it has actually compiled and run; a clear guide is not evidence of an implemented API.
Use a traceability table or export inventory only when drift or scope makes it useful.

Compare the proposed contract with current consumers and documentation. Name affected signatures,
examples, tests, stored formats, and ADRs; distinguish proposed supersession from an accepted change.
Choose compatibility, replacement, rollout, and rollback strategies from the actual commitments.
Parallel replacement, shims, and immediate removal are options with costs, not universal rules.

End with the usable contract, agreed choices, unresolved blockers, and evidence still needed. When
the user wants implementation planning, writing-plans can turn the settled requirements into tasks.
Do not force a new skill invocation, agent handoff, implementation, or publication.
