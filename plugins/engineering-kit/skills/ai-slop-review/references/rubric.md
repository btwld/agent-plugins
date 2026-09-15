# AI slop rubric

The fourteen patterns a finder may report, the decision test for each, which lens owns it, and
what is never a finding. Load the lens block you are about to apply; paste it verbatim into a
delegated finder or validator prompt so the agent never has to open this file.

The bar for every pattern: report only when the code is worse than a careful engineer in this
language would ship. "An LLM wrote this" is not a finding. Voice alone is not a finding.

## Pattern IDs

Severity defaults come from the rule. A finder may move severity one step with a one-sentence
reason in `why`. Lens letters: **C** comments and docs, **K** code shape, **T** tests,
**W** repo-wide sweep.

| ID | Lens | Pattern | Decision test | Default |
|----|:--:|---------|---------------|:--:|
| S1 | C, T | Comment restates the code | Delete the comment. Did the reader lose anything the next line or the signature does not already say? `/// The count.` on `int get count`; `// increment` above `i++`; a class doc that lists the class's own fields or names the implementation type it wraps. | P3 |
| S2 | C | Documented non-decision | Does the comment justify a choice nobody would question (`// use a list here`, `// check for null first`)? Keep comments that record a real constraint: ordering that matters, encoding or Unicode, ABI, platform divergence, a rejected alternative. | P3 |
| S3 | C, T | Tutorial or chat voice | Is the phrasing addressed to a reader being taught rather than stating a fact? "We then…", "This function will…", "Note that…", "It's important to…", "simply", "make sure", `Note:` / `Important:` prefixes, emoji in comments, a block comment used as documentation where the language's doc convention is a line form. If the content is useful, the fix is rewrite, not delete. | P3 |
| S4 | C | Tag-style docs against the language convention | `@param` / `@returns` / `@throws` or `Args:` / `Returns:` blocks in a language whose style guide asks for prose and bracketed identifiers (Dart, Rust, Go). Not a finding where tags are the convention (JSDoc, Javadoc, Google-style Python docstrings). | P3 |
| S5 | K, T, W | Blanket or premature catch | Could the guarded code throw here, and does the handler report or rethrow? Report `try` around code that cannot throw; a catch-all that logs-and-continues or returns a default silently; catching the language's base error type. Exempt: error boundaries and IO, process, FFI, or network edges that surface the failure. | P2, P1 if it hides a bug |
| S6 | K | Impossible defensive code | Can the guarded state occur given the declared types and the narrowing in scope? Null checks on non-nullable values, optional chaining after a definite value, `?? x` on a non-nullable, asserts that restate the type system, empty `else {}`. | P2 |
| S7 | K | Over-abstraction | How many implementations or call sites? A factory, strategy, or wrapper with one implementation; a class around a three-line function; a type alias used once; `Manager` / `Helper` / `Util` with no domain meaning; a one-member interface where a function would do. Count and state the number in `why`. | P2 |
| S8 | K | Scope creep in a unit | List the concerns one function handles. Report when it fetches, transforms, validates, and notifies in one body, or exceeds roughly 80 lines of mixed concerns, or nests so the happy path is hidden. Name the concerns. | P2 |
| S9 | K, T, W | Generic naming | Does the type already say what the name says, and do neighboring files use a domain word? `data`, `result`, `temp`, `value`, `item`, `info`, `handler`, `processX`, `handleX`, `doX`; a `get` prefix on a property-like method; test names such as "should work" that state no behavior. Framework-domain names (`FocusManager`, `EventHandler` in an event system) are not generic. | P3 |
| S10 | T | Fake or hollow test | If the code under test were broken in the obvious way, would this test fail? Asserts on the fake or mock rather than behavior; `expect(x, x)`; "does not throw" or "is not null" as the only assertion; an expected value computed by re-running production logic; a body with no assertion; happy path only where a failure mode is obvious. Also a coverage gap: a public entry point of the unit under test with an obvious failure path (a catch that releases and rethrows, a rejection branch) and no test at all, especially when the file wires up mocks for it and never asserts on them. | P2, P1 if it masks a real failure |
| S11 | K | Superseded idioms the linter does not catch | Constructs the language has moved past that no enabled lint flags: redundant `new`, explicit `= null`, `== true`, `.length == 0`, callback loops where a `for` reads better, redundant `this.` or `const`, Hungarian or `kFoo` names, `late` or lazy init where a direct initializer works. Check the linter configuration first. | P2 |
| S12 | K, T, W | Dead ceremony | Unused private helpers; a lint suppression for a rule that is not enabled or no longer fires; TODOs with no owner or issue; a utility duplicated from elsewhere in-tree; configuration knobs with one value; commented-out code; compatibility shims or "legacy" aliases in code that has no compatibility promise. | P2 |
| S13 | K, T | Architecture mismatch | Does the code cross a boundary the repository states? A UI layer calling native or IO directly; a reinvented framework primitive (focus, routing, hit testing, text editing) where one exists; a new test harness or fake that re-implements framework behavior instead of using the documented harnesses; a package importing another package's private modules. Derive the boundaries from the repository's own instructions; do not invent them. | P1 |
| S14 | C, W | Markdown slop | Filler ("In this section we will…"), the heading restated in the first sentence, marketing adjectives (powerful, seamless, comprehensive, robust), emoji headers, bold on every other phrase, references to APIs that no longer exist, placeholder text. | P3 |

Lens **T** also carries S1 and S3 for comments inside tests, S5 for catch-alls that swallow a test
failure, S9 for empty test names, S12 for dead ceremony in tests, and S13 for a new harness.
Lens **W** carries whatever its hit lists cover.

## Never report

- Anything the configured linter, analyzer, or formatter already enforces. Name the rule and move on.
- The existence of a doc comment on a public member when the repository requires one. Judge content only.
- Any comment that explains **why**: ordering, invariants, encoding, ABI, a rejected alternative, a
  bounded leak, a backstop that is normally unreachable. First-person "we" inside a why-comment is fine.
- Numbered steps where each step states an ordering constraint.
- Test names that read as specifications, however long.
- Repetition that is the test's point (tables of cases, parameterized inputs).
- Emoji or unusual Unicode inside string literals; they are usually test data.
- Golden, fixture, generated, or vendored files.
- Formatting, line length, import order.
- Performance without a measured budget.
- A pattern used consistently as a file's convention (section dividers in a large constants table):
  at most one file-level P3 for the whole file.

## Severity and confidence

- **P1** hides a bug, fakes safety, or crosses a stated layer boundary. Must survive validation at
  `high` confidence to appear in the report as P1.
- **P2** maintenance tax. Fix when the file is next touched or in a cleanup pass.
- **P3** noise. Clusters in one file matter; single instances rarely do.
- `high`: named pattern, cited guideline, quoted snippet, and the finder checked the context (types,
  call sites, linter config). `medium`: could be house style. `low`: smell only; validators reject
  it unless two finders hit the same location.

## Guideline sources by language

A finding cites a guideline so a reader can check the charge against something other than the
finder's taste. Use the target language's canonical guide; fall back to the general sources.

| Language | Guideline source |
|---|---|
| Dart | Effective Dart (Documentation, Usage, Design). Formatting belongs to `dart format`, never a finding. |
| TypeScript / JavaScript | Google TypeScript Style Guide; the project's ESLint config for what is already enforced. |
| Python | PEP 8, PEP 257, Google Python Style Guide; `ruff` or `flake8` config for what is enforced. |
| Go | Effective Go, Go Code Review Comments; `go vet` and `staticcheck` for what is enforced. |
| Rust | Rust API Guidelines; `clippy` configuration. |
| Any | Google "What to look for in a code review" (comments explain why, not what); the repository's own CLAUDE.md, AGENTS.md, CONTRIBUTING, or architecture docs. |

General sources the rubric draws on, for citation in `guideline`:

- G-Research, "Building a code review tool: the LLM patterns that actually work": rules are the only
  source of truth; recall and precision are separate passes; severity comes from the rule.
- Heym, "Adversarial code review": finder, challenger, orchestrator; the challenger has no stake in
  the finder's conclusion; structured data between agents.
- Datadog, "Using LLMs to filter out false positives": the filter needs the finding plus the code
  and must give a reason.
- "An Endless Stream of AI Slop" (arXiv 2603.27249): maintainer tells are emoji, step narration,
  verbose style, test subversion, fictional integrations.
- "AI-Generated Smells" (arXiv 2605.02741): generated volume correlates with smell density; long
  methods and extra layers are findings even when tests pass.
- Potapov, "AI slop detection"; Sailop, "23 tells of AI-generated code"; TechDebt.fail, "AI code
  review": the pattern catalog behind S1 through S12.

## Building repo calibration

Before finders run, write four to eight calibration examples from the actual repository: two or
three real lines to **report** with the pattern and fix, and two or three real lines to **keep**
that a naive reader would flag (a why-comment, a justified backstop, numbered ordering steps, a
domain name that looks generic). Put them in the finder prompt. Over-reporting on S1 and S3 is the
known failure mode; the keep examples pull the line back. Empty calibration produces noisy finders.
