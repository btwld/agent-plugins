---
name: writing-for-humans
description: Use when writing, editing, or reviewing human-facing technical and project prose—including documentation, specs, capability and user-story documents, Linear or issue-tracker descriptions, procedures, READMEs, and technical explanations—using Simplified Technical English (ASD-STE100) and single-source linking. Do not use for authoring agent instructions such as SKILL.md, AGENTS.md, or CLAUDE.md (use writing-for-agents) or formalizing SBVR business rules (use sbvr).
---

# Writing for Humans

Write clear, direct prose for the intended human reader. Keep the requested format and technical detail while making specifications, guides, and tracker items easy to scan and maintain.

## Clear prose (ASD-STE100 principles)

Apply these selected ASD-STE100 principles when drafting or revising prose:

- **Use consistent terms** for the same concepts. Follow the repository's existing vocabulary instead of rotating synonyms.
- **Keep sentences short:** aim for at most **20 words** in procedures and **25 words** in descriptions. Preserve meaning when brevity conflicts with precision.
- **Use active voice.** Name the actor performing the action. Do not invent an actor when the source leaves responsibility unknown.
- **Write instructions as commands,** with one action per sentence unless actions must happen together.
- **Put conditions before the actions they govern** (for example, *"If the token is expired, refresh the session"*). Keep required actions out of informational notes.
- **Keep each paragraph on one topic.** Make pronoun references unambiguous and prefer simple verb constructions.
- **Retain established technical nouns** ending in `-ing` (such as *billing*, *routing*, or *logging*); do not rewrite them merely to avoid `-ing`.
- **Prefer American English spelling** unless the task or an exact identifier requires otherwise.

### Normative precision

- Preserve obligations, permissions, negation, conditions, exceptions, quantifiers, and ownership.
- Keep quotations, defined terms, requirement IDs, code identifiers, commands, numbers, and citations intact.
- Do not weaken requirement force or project status to simplify a sentence.

## Structure that scans fast

- **Lead with purpose and boundary:** Open specs, capabilities, and guides with 2–5 sentences explaining what the subject does, who uses it, and what it leaves out.
- **Use tables when fields repeat:** When the same attributes repeat across 3 or more items—such as status values and transitions, role permissions, or system mappings—use a table instead of repeating sentence templates.
- **Structure capabilities and user stories around verifiable outcomes:**
  - **User story:** One short paragraph stating *who* wants *what* and *why*.
  - **Expected outcome:** One sentence stating what is true when the story succeeds.
  - **Starting conditions:** Concrete prerequisites that hold before the flow begins.
  - **Flow:** Numbered steps showing what the actor does and how the system responds.
  - **Acceptance checks:** Concrete *Given / When / Then* checks covering both success paths and refusal or failure cases.

## Link, don't copy (docs and issue trackers)

Keep requirements, acceptance checks, defaults, and status rules in **one canonical document** so updates never drift across copies:

- **Overview and index pages:** State what a target document covers in one sentence and link to it instead of repeating its rules.
- **Linear and issue trackers:** Track **execution state and ownership** (status, assignee, priority, cycle/milestone, blockers, PR links) in the tracker, and keep specification prose in the canonical doc:
  - **Initiative or Project:** State the goal, scope boundary, and links to canonical capability or architecture specs. Do not paste full specs into project descriptions.
  - **Parent issue (capability / feature) and sub-issue (story / task):** Include a 1-line outcome summary and a direct link to the canonical spec or story section, plus only ticket-specific delivery notes (such as rollout order or environment blockers). Do not copy full acceptance-check lists or requirement tables into tickets where they go stale.

## Final check

Before returning the work, compare it with the source to confirm no obligations, conditions, negations, or identifiers changed meaning. Apply edits within the requested scope and return the content directly without routine compliance scores or process commentary.

This is an STE-informed guide based on Issue 9, not the complete standard or controlled dictionary. For official standard references and compliance verification notes, see [`references/sources.md`](references/sources.md).
