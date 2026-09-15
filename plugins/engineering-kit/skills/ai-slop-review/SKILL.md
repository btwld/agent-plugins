---
name: ai-slop-review
description: >-
  Use when the user wants code, comments, docs, or tests audited for AI-generated slop across a
  PR, directory, package, or whole repository: restating or tutorial-voice comments, blanket
  catches, impossible defensive code, over-abstraction, generic names, dead ceremony, stale lint
  suppressions, hollow tests, or markdown filler. Trigger on "AI slop", "looks LLM-generated",
  "Copilot/Claude cruft", "over-commented", "defensive noise", or "are these tests real". Runs a
  review-only, evidence-gated finder-then-validator pass and reports only findings that survive
  with path, lines, snippet, and fix. Prefer adversarial-change-review for a keep/reject verdict
  on one change's behavior and native diff review for ordinary bug-finding. Review-only unless fixes are explicitly requested.
---

# AI Slop Review

Find the places where generated code is worse than a careful engineer would ship, prove each
one with a cited snippet, try to disprove it, and report only what survives. The default output is a
findings report; implement fixes only when the user has requested them. The bar for every finding is the code, never its origin: "an LLM
wrote this" is not a finding, and neither is voice alone.

## Size the review to the scope

Start from the actual target: a diff range, pull request, directory, package, or repository.
Estimate the scope and choose a proportionate execution mode. Work inline or in sequential
slices by default. Use subagents only when permitted and useful, respecting the user's model,
cost, and concurrency preferences. A large line count alone does not authorize delegation.
For a large scope, [orchestration.md](references/orchestration.md) provides slicing and evidence
contracts that also work sequentially. Preserve coverage and report unread files honestly.

Record the starting worktree state and leave unrelated edits in place. A read-only review does
not require stashing, resetting, committing, or cleaning the working tree.

For a diff, only touched hunks are in scope. Read the whole file for context, because slop is
judged against the file's conventions, but a finding on an untouched line carries
`"preexisting": true` and lands in a separate optional bucket. A pull request is not
responsible for the cruft around it.

## Establish repo facts before reading

Inspect the relevant repository conventions before classifying findings. Record the facts
needed for the review, sharing them with any permitted delegated reviewers:

- **Linter and formatter configuration** and what it enforces. Anything the analyzer already
  flags is out of scope; name the rule and move on.
- **Doc-comment requirements.** When the repository requires a doc on every public member, its
  existence is never slop; only its content can be.
- **Layer and boundary rules** from `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING`, or architecture
  docs. S13 architecture findings come only from boundaries the repository states.
- **Test harnesses** the repository documents. A harness or fake the repository does not
  document is a finding; the documented ones are not.
- **Out-of-scope paths:** generated, vendored, golden, third-party, and anything the user excludes.
- **Compatibility promises.** A prerelease removes obsolete shapes; a stable library shims them.
  Legacy aliases are S12 only where no promise exists.

For a broad or uncertain review, use representative report and keep examples as described in
[rubric.md](references/rubric.md). Scale calibration to the task; do not manufacture examples to
meet a quota. Over-reporting on restating comments and chat voice is a known failure mode.

## Run the mechanical sweep first

With `<skill>` set to this skill's directory and `<workspace>` a directory outside the repo:

```bash
git diff --name-only <range> > <workspace>/changed.txt            # diff scope only
python3 <skill>/scripts/sweep.py --root . --out <workspace> [--files <workspace>/changed.txt]
```

The sweep writes hit lists per rubric pattern (catch-alls, suppressions, step narration, chat
voice, history narration, tag-style docs, helper and manager names, emoji, commented-out code,
legacy shims), stale Dart lint suppressions when `analysis_options.yaml` is present, and
per-test-file hints (marketing names, Arrange/Act/Assert narration, does-not-throw-only,
tautologies, not-null-only, expected values computed from the input instead of a literal, files
with more tests than assertions). Hits are leads. Every hit
is triaged as reported or not_slop with a one-line reason; a hit you cannot justify is not_slop.
Searches run once and cannot miss a pattern; the judgment is what the finder adds.

## Find

Load the lens block you are applying from [rubric.md](references/rubric.md) and work one lens
at a time: comments and docs (C), code shape (K), tests (T). Mixing lenses in one pass produces
shallower reads and a validator that cannot specialize.

- Read every in-scope file to its last line and keep a `{path, lines_read}` ledger. File-read
  tools truncate long files; the ledger makes a partial read visible instead of silent.
- For each candidate, name the pattern and apply its decision test before deciding. If the test
  does not clearly fail, do not report. The tests are questions ("delete the comment; did the
  reader lose anything?", "if the code were broken the obvious way, would this test fail?"),
  and the answer goes in `why`.
- For S5 and S6, read the types and narrowing in scope. For S7, count the implementations or
  call sites and state the number. For S12 suppressions, check the linter configuration.
- For tests, read each body, then invert the view: list the unit's public entry points and which
  tests exercise them. An entry point with an obvious failure path and no test is S10 too, and
  reading test bodies alone never surfaces it.
- Every finding carries path, start and end line, a verbatim snippet of at most four lines, the
  guideline it violates, a one- or two-sentence `why`, and a one-sentence fix. Severity defaults
  from the rule; move it one step only with a reason.
- An empty findings list is a correct result for clean code. Do not manufacture findings to
  justify the pass.

Write findings as JSON in the finder contract from [orchestration.md](references/orchestration.md)
even for an inline review, one file per lens under `<workspace>/findings/` with agent ids such
as `C-inline`; the gate and the validator both read that shape.

## Gate every citation

```bash
python3 <skill>/scripts/check_findings.py --root . --no-slices [--diff-range <range>] <workspace>/findings/*.json
python3 <skill>/scripts/check_findings.py --root . --workspace <workspace> <workspace>/findings/*.json   # delegated
```

The gate verifies that each snippet exists within one line of its cited range, the pattern is in
the agent's lens, severity and confidence are valid, every slice file was read to its last line,
and, with a diff range, every finding sits inside a changed hunk or is marked preexisting. Fix or
drop what fails before validation; a validator's time is the most expensive in the run.

## Validate by trying to disprove

The second pass sees only the structured fields: id, path, lines, pattern, severity, confidence,
snippet, guideline, fix. Never the finder's `why`. Its job is to defeat each charge, in order:
is it a why-comment; does a doc requirement or caveat justify it; is the catch at a boundary that
reports; is the guarded state actually impossible given the types; how many implementations are
there; would the test fail on the obvious break; does the linter already enforce it; is it the
file's consistent convention. Verdicts are confirm, downgrade, reject, or reclassify, each with a
one-sentence reason grounded in the cited code.

Inline, do this yourself after finishing the find pass, from the stripped view, and be harsh on
S1, S2, S3, and S9. Delegated, one validator per roughly three finders of the same lens, using the
validator prompt in [prompts.md](references/prompts.md).

Judge validation by its evidence and counterarguments, not a required rejection rate. All findings
may legitimately survive, or none may. Revisit a pass when concrete unsupported conclusions or
missed counterevidence justify it. A P1 survives only at high confidence.

## Report

Lead with confirmed P1s, then P2s grouped by file, each with pattern id, path, lines, snippet,
and fix, then P3s clustered by file with counts. The pattern id is what lets a team batch fixes
and check a charge against the rubric, so keep it in the report and not only in the JSON. Include a few sample rejections with their reasons so the reader
can judge the validation, the files with zero findings, and anything not fully read. For a
delegated run, write `REPORT.md` in the workspace with the per-lens and per-pattern counts from
orchestration.md.

Keep review-only requests read-only. If the user already requested fixes, apply supported changes
within that scope without asking again. Comment deletions can be grouped; behavior changes need
focused verification of the affected and preserved behavior. When
the user then wants a keep-or-reject judgment on such a fix, that is adversarial-change-review's
job, not this skill's.

## Supporting files

| Read | When |
|---|---|
| [rubric.md](references/rubric.md) | Before any find or validate pass: the fourteen patterns, decision tests, never-report list, severity, guideline sources by language, calibration method |
| [orchestration.md](references/orchestration.md) | Large reviews: optional slicing, sequential or permitted delegated work, output contracts, validation, and coverage |
| [prompts.md](references/prompts.md) | Composing self-contained finder, sweep, and validator prompts for subagents |
| `scripts/slice.py` | Delegated runs: cut the scope into slices one agent can read in full, with a coverage check |
| `scripts/sweep.py` | Every run: mechanical hit lists and test hints |
| `scripts/check_findings.py` | Every run: the citation, lens, coverage, and diff-range gate for finder and validator JSON |
| `scripts/_scope.py` | Not run directly: the file-gathering and language classification the three scripts share |
