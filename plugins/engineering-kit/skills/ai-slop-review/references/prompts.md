# Finder, sweep, and validator prompts

Templates for delegated agents. Fill every `{PLACEHOLDER}`; paste the lens rules from
`rubric.md` where marked so each prompt is self-contained.

## Contents

1. [Placeholders](#placeholders)
2. [Finder, lens C (comments and docs)](#finder-lens-c-comments-and-docs)
3. [Finder, lens K (code shape)](#finder-lens-k-code-shape)
4. [Finder, lens T (tests)](#finder-lens-t-tests)
5. [Sweep, lens W](#sweep-lens-w)
6. [Validator](#validator)

Design choices these templates encode, so edits keep them:

- Each rule is a question the agent answers per candidate, not a label to pattern-match.
- Negative examples are inline; over-reporting on S1 and S3 is the known failure mode.
- The reading protocol is chunked and produces a `lines_read` ledger, because file-read tools
  truncate long files and a partial read must be visible.
- "Write the JSON first, summarize second" so a truncated reply cannot lose the artifact.
- Re-verification before writing: the gate catches a bad citation, but the agent should catch it first.

## Placeholders

| Placeholder | Content |
|---|---|
| `{ROOT}` | absolute repository path |
| `{REPO_SUMMARY}` | one line: what the repository is and its main language |
| `{REPO_FACTS}` | bullets: linter and what it enforces, doc-comment requirement, layer rules, test harnesses, out-of-scope paths |
| `{RULES_<LENS>}` | the lens's rows from the rubric table, rewritten as the question-form rules shown in the examples |
| `{NEVER}` | the rubric's never-report list |
| `{CALIBRATION}` | two or three real report examples and two or three real keep examples from this repository |
| `{GUIDELINE_SOURCE}` | the language's style guide name, for the `guideline` field |
| `{ID}`, `{SLICE_PATH}`, `{HINTS_PATH}`, `{OUTPUT_PATH}`, `{INPUTS_PATH}`, `{SWEEP_DIR}` | per-agent paths |
| `{DIFF_NOTE}` | empty for a repository scope; for a diff scope: "Only lines inside the changed hunks of `<range>` are in scope. A finding outside them must carry `"preexisting": true` or be dropped." |

## Finder, lens C (comments and docs)

```
You are one finder in a two-pass review of {REPO_SUMMARY} at {ROOT}.

Your single job: find comments and documentation that a careful engineer would delete or
rewrite. Nothing else. Do not review code structure, error handling, naming, or tests; other
agents own those.

READ-ONLY. Do not edit, create, or delete any file except your output file. Do not run the
linter, tests, or formatters.

AGENT_ID: {ID}
SLICE: read every file listed in {SLICE_PATH}
OUTPUT: {OUTPUT_PATH}
{DIFF_NOTE}

== Repo facts you must respect ==
{REPO_FACTS}

== Rules (report only these; cite the id) ==
{RULES_C}

Also apply the language's doc-comment form: a type doc starts with a noun phrase, not "This
class…"; a boolean doc starts with "Whether"; the first sentence is a one-line summary in its
own paragraph. Report a form violation as S1 or S3 with the guideline named.

== Never report ==
{NEVER}

== Calibration ==
{CALIBRATION}

== Reading protocol ==
1. Read the slice list. For each file, note its line count.
2. Read every file to its last line. For files over 800 lines, read in chunks with offset and
   limit and keep going until the last line. Record {path, lines_read} as you finish each file;
   lines_read must equal the real line count or the file will be sent back.
3. For each candidate, write down the rule id and apply that rule's test before deciding. If
   the test does not clearly fail, do not report.
4. Severity defaults to P3 for this lens. Raise to P2 only for a dense cluster (five or more in
   one file) and say so in why.
5. Confidence: high = named pattern, guideline, snippet; medium = could be house style;
   low = smell only (validators reject these).

== Output ==
Write JSON to OUTPUT with exactly this shape:
{
  "agent_id": "{ID}",
  "files_reviewed": [ {"path": "...", "lines_read": 0} ],
  "files_skipped": [],
  "hints_triaged": [],
  "notes": "",
  "findings": [
    { "id": "{ID}-001", "path": "...", "start_line": 0, "end_line": 0,
      "pattern": "S1", "severity": "P3", "confidence": "high",
      "snippet": "verbatim, at most 4 lines",
      "guideline": "{GUIDELINE_SOURCE}: <rule>",
      "why": "one or two sentences applying the test",
      "fix": "one sentence: delete / rewrite as … / move to …" }
  ]
}

Before writing: re-open every cited range and confirm the snippet is there verbatim. Remove
any finding you cannot re-find. An empty findings list is a correct result for a clean slice;
do not manufacture findings.

Then reply in at most 8 lines: files read, files not fully read and why, finding counts by
pattern, anything that blocked you.
```

## Finder, lens K (code shape)

```
You are one finder in a two-pass review of {REPO_SUMMARY} at {ROOT}.

Your single job: find code shapes that a careful engineer would simplify or remove. Do not
review comment or documentation wording; another agent owns that. Do not review tests; another
agent owns those.

READ-ONLY. Do not edit, create, or delete any file except your output file. Do not run the
linter, tests, or formatters.

AGENT_ID: {ID}
SLICE: read every file listed in {SLICE_PATH}
OUTPUT: {OUTPUT_PATH}
{DIFF_NOTE}

== Repo facts you must respect ==
{REPO_FACTS}

== Rules (report only these; cite the id) ==
{RULES_K}

== Never report ==
{NEVER}

== Calibration ==
{CALIBRATION}

== Reading protocol ==
1. Read the slice list. For each file, note its line count.
2. Read every file to its last line; chunk files over 800 lines with offset and limit until
   the last line. Record {path, lines_read}; it must equal the real count or the file is sent back.
3. For each candidate, name the rule and apply its test. For S5 and S6 read the types and
   narrowing in scope before deciding. For S7 count the implementations or call sites with a
   search and state the number in why. For S12 suppressions, check the linter configuration.
4. Severity defaults from the rule. Move one step only with a reason.
5. Confidence: high = pattern, guideline, snippet, and you checked the context (types, call
   sites, config); medium = could be house style; low = smell only.

== Output ==
Same JSON shape as the C finder, with "pattern" drawn from this lens and "why" stating the
count or type fact you checked. Re-open every cited range before writing. An empty findings
list is a correct result for a clean slice.

Then reply in at most 8 lines: files read, files not fully read and why, finding counts by
pattern, anything that blocked you.
```

## Finder, lens T (tests)

```
You are one finder in a two-pass review of {REPO_SUMMARY} at {ROOT}.

Your single job: find tests in your slice that do not actually test behavior, plus dead
ceremony and comment noise inside test files.

READ-ONLY. Do not edit, create, or delete any file except your output file. Do not run the
tests, linter, or formatters.

AGENT_ID: {ID}
SLICE: read every file listed in {SLICE_PATH}
HINTS: {HINTS_PATH}
  Mechanical hits in your slice: marketing test names, Arrange/Act/Assert narration,
  does-not-throw-only, tautologies, not-null-only, expected values computed from the input,
  suppressions, and files whose test count exceeds their assertion count. Every hint must appear in hints_triaged as "reported" (with
  the finding id) or "not_slop" (with a one-line reason). Hints are leads, not findings; a hint
  you cannot justify is not_slop.
OUTPUT: {OUTPUT_PATH}
{DIFF_NOTE}

== Repo facts ==
{REPO_FACTS}
(Include the documented test harnesses here. A new harness or a fake that re-implements
framework behavior is S13.)

== Rules (report only these) ==
{RULES_T}

== Never report ==
{NEVER}

== Reading protocol ==
1. Read the slice list and the hints file.
2. Read every file to its last line; chunk files over 800 lines. Record {path, lines_read}.
3. For each test body, ask the S10 question: if the code under test were broken in the obvious
   way, would this test fail? For a hint, open the cited line and decide; record the outcome in
   hints_triaged either way.
4. Then invert the view: list the public entry points of each unit under test and which tests
   exercise them. An entry point with an obvious failure path and no test at all is S10 too,
   cited at the untested function, and it is easy to miss when you only read test bodies.
5. Severity defaults from the rule; move one step only with a reason.

== Output ==
Finder JSON shape with hints_triaged filled:
  "hints_triaged": [ {"hint": "path:line", "outcome": "reported"|"not_slop",
                      "finding_id": "..."|null, "reason": "..."} ]
For S10 the "why" names the obvious break this test would not catch. Re-open every cited range
before writing. Empty findings is a correct result for a clean slice.

Then reply in at most 8 lines: files read, hints triaged (reported / not_slop), finding counts
by pattern, anything that blocked you.
```

## Sweep, lens W

```
You are the repo-wide sweep agent in a two-pass review of {REPO_SUMMARY} at {ROOT}.

Your single job: triage pre-computed search hits that only make sense repo-wide, and turn the
ones that fail the rubric into findings. You do not read whole files; you open each hit with
enough context to judge it.

READ-ONLY. Do not edit, create, or delete any file except your output file.

AGENT_ID: W-1
INPUT: every file in {SWEEP_DIR} except hints-*.txt. SUMMARY.txt has counts. Each hit list is
  named by rubric id and pattern, one hit per line as path:line: text.
OUTPUT: {OUTPUT_PATH}
{DIFF_NOTE}

== Rules by hit list ==
S12-stale-suppressions.txt  Already computed: suppressions naming a rule no configuration
  enables. One finding per rule with the file list in fix. P2, high.
S12-suppressions.txt  For the remaining suppressions, sample each rule name: is there a
  justification comment? Is the rule even enabled? One finding per rule suppressed without
  justification in more than three files. P2.
S5-catch-all.txt  Open each hit. Report only handlers that swallow: no rethrow, no report, no
  documented boundary. One finding per site. P2; P1 if it hides a real failure.
S1-S3-step-narration.txt, S3-section-dividers.txt, S3-chat-voice.txt,
S2-history-narration.txt, S1-this-class-docs.txt  Open each hit; apply the comment test:
  delete it, did the reader lose anything? Report only clear failures. Numbered steps that
  encode ordering are not findings. Dividers used consistently in one large constants file are
  one file-level P3 at most.
S12-legacy-compat.txt, S12-todo.txt, S12-commented-out-code.txt  Report shims, aliases,
  orphan TODOs, and commented-out code. P2.
S4-tag-style-docs.txt, S3-block-comment-docs.txt  Report every real hit in a language whose
  guide asks for prose docs; skip languages where tags are the convention.
S9-helper-manager-names.txt  Report only names with no domain meaning.
S3-S14-emoji.txt  Emoji inside string literals in tests is data. Report emoji in comments or
  Markdown prose only.

Every hit must appear in hints_triaged as reported (with finding id) or not_slop (with a
one-line reason). Aggregate identical repo-wide patterns into one finding whose snippet is the
pattern and whose fix lists the files.

== Output ==
Finder JSON shape, with files_reviewed listing every hit list you processed as {path,
lines_read}. Re-open every cited range before writing. Reply in at most 8 lines with hit
counts triaged and findings by pattern.
```

## Validator

```
You are a validator in a two-pass review of {REPO_SUMMARY} at {ROOT}. Finders have proposed
findings; your job is to DISPROVE them. A validator that confirms everything has failed.
Expect to reject or downgrade a real share.

READ-ONLY. Do not edit, create, or delete any file except your output file.

AGENT_ID: {ID}
LENS: {LENS}
INPUTS: {INPUTS_PATH}
  (fields: id, path, start_line, end_line, pattern, severity, confidence, snippet, guideline,
  fix. There is no finder reasoning; reconstruct the charge from the code.)
OUTPUT: {OUTPUT_PATH}

== The rules the finder was allowed to use ==
{RULES_<LENS>}

== Never report ==
{NEVER}

== Procedure, per finding ==
1. Open the file at the cited lines with at least 20 lines of context on each side. If the
   snippet is not there, verdict reject, reason "snippet not at cited lines".
2. State the charge in your own words from the code alone.
3. Try to defeat it, in this order:
   a. Is it a why-comment (ordering, invariant, encoding, ABI, rejected alternative)? Reject.
   b. Does a doc-comment requirement or a real caveat justify the doc? Reject.
   c. For S5: is the catch at an IO, process, FFI, or network edge, and does it report or
      rethrow? Reject.
   d. For S6: read the declared types and narrowing; is the state actually impossible? If not,
      reject.
   e. For S7: count implementations or call sites yourself. If more than one, reject.
   f. For S10: name the obvious break; would the test fail? If yes, reject.
   g. Does the configured linter already enforce it? Reject and name the rule.
   h. Is the pattern the file's consistent convention? Downgrade to P3 at file level, or reject
      if already reported for that file.
4. Verdict: confirm | downgrade (give new severity) | reject | reclassify (give new pattern).
   reason is one sentence that quotes or paraphrases the code at the cited lines. A reason that
   could apply to any finding is not a reason.
5. Be harsh on S1, S2, S3, S9: these are over-reported. Be careful with S5, S10, S13 when the
   bug-hiding is real.

You may add missed findings, P1 or P2 only, only in files that appear in the inputs, using the
finder schema plus "lens": "{LENS}".

== Output ==
{
  "agent_id": "{ID}",
  "inputs": [ "..." ],
  "reviews": [ { "finding_id": "...", "verdict": "confirm|downgrade|reject|reclassify",
                 "severity": "P1|P2|P3", "pattern": "S..", "confidence": "high|medium|low",
                 "reason": "one sentence grounded in the cited code" } ],
  "missed": []
}

Every input finding id gets exactly one review. Write the file, then reply with counts
(confirm / downgrade / reject / reclassify / missed) and the two rejections you are most sure of.
```
