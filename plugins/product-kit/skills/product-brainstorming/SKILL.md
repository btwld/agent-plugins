---
name: product-brainstorming
description: "Use when exploring product opportunities, generating solution alternatives, or testing assumptions before choosing a direction. Follow the requested mode and output size; use write-prd for an already chosen feature."
---

<!-- Adapted from anthropics/knowledge-work-plugins by Leo Farias. See ../../SOURCES.md for source attribution and license. -->

# Product Brainstorming

Help the user find useful options and expose assumptions that could change the decision.

## Establish the frame

Use the supplied problem, audience, evidence, and constraints. Ask only for missing context that would materially change the exploration. If the user requests ideas immediately, provide ideas with stated assumptions.

Choose the useful mode: explore an unclear problem, generate alternatives for a defined problem, stress-test a proposed solution, or compare strategic bets. Change modes as the conversation changes; do not require a sequence.

## Explore

- Separate the user's underlying job from the current proposed feature. Consider who experiences the problem, when, and what they do today.
- Generate meaningfully different approaches within the requested count. Vary scope, effort, product versus process, and short versus long term. Consider removing a step when that could solve the problem.
- Use a technique only when it opens a useful angle: invert the problem, borrow an analogy, split it into parts, or change the user perspective.
- Check each proposed option against supplied constraints. If an option needs a capability whose existence is unknown, label the dependency instead of implying it already fits.
- Treat hard constraints as real. Label an intentionally unconstrained thought experiment and return to feasible options before recommending action.
- Challenge a consequential assumption with a reason and evidence. Do not insist on further divergence after the user has chosen to converge.

## Converge

Compare serious options using the user's decision criteria. Identify the riskiest assumption and the smallest useful way to test it. Distinguish evidence from hypotheses; synthetic opinions are idea inputs, not customer validation.

Return the requested artifact: a list of ideas, a short comparison, a recommendation, or a conversational response. A list-only request does not require an interview, PRD, or extra follow-up offers.
