# AI slop rubric

Optional pattern tests for a deeper quality audit. Ordinary reviews already consider
unnecessary code and hollow tests and must not skip those checks if this file stays unloaded.

The sixteen patterns a finder may report, the decision test for each, which lens owns it, and
what is never a finding. Load the lens block you are about to apply; paste it verbatim into a
delegated finder or validator prompt so the agent never has to open this file.

The bar for every pattern: report only when the code is worse than a careful engineer in this
language would ship. "An LLM wrote this" is not a finding. Voice alone is not a finding.

## Pattern IDs

Pattern defaults are starting points, not severity mandates. Assign severity from the
demonstrated impact and explain it in `why`. A hint must survive contextual validation. Lens letters: **C** comments and docs, **K** code shape, **T** tests,
**W** repo-wide sweep.

| ID | Lens | Pattern | Decision test | Default |
|----|:--:|---------|---------------|:--:|
| S1 | C, T | Comment restates the code | Delete the comment. Did the reader lose anything the next line or the signature does not already say? `/// The count.` on `int get count`; `// increment` above `i++`; a class doc that lists the class's own fields or names the implementation type it wraps. | P3 |
| S2 | C | Documented non-decision | Does the comment justify a choice nobody would question (`// use a list here`, `// check for null first`)? Keep comments that record a real constraint: ordering that matters, encoding or Unicode, ABI, platform divergence, a rejected alternative. | P3 |
| S3 | C, T | Authoring residue or misleading commentary | Does the comment contain leftover assistant/editor instructions, false claims, or narration that obscures the contract? Preserve legitimate rationale, tutorials, prompt templates, and security-test inputs. Voice alone is not evidence. | P3 |
| S4 | C | Tag-style docs against the language convention | `@param` / `@returns` / `@throws` or `Args:` / `Returns:` blocks in a language whose style guide asks for prose and bracketed identifiers (Dart, Rust, Go). Not a finding where tags are the convention (JSDoc, Javadoc, Google-style Python docstrings). | P3 |
| S5 | K, T, W | Blanket or premature catch | Could the guarded code throw here, and does the handler report or rethrow? Report `try` around code that cannot throw; a catch-all that logs-and-continues or returns a default silently; catching the language's base error type. Exempt: error boundaries and IO, process, FFI, or network edges that surface the failure. | P2, P1 if it hides a bug |
| S6 | K | Unnecessary defensive code | Can this state occur at runtime given callers, narrowing, external inputs, and compatibility obligations? Prove the guard redundant on this path; annotations alone do not establish runtime validity. | P2 |
| S7 | K | Over-abstraction | What semantics, lifecycle, boundary, or test seam does this layer own? Count callers/implementations as context, then demonstrate unnecessary indirection and a simpler compatible alternative. A single caller is not sufficient evidence. | P2 |
| S8 | K | Scope creep in a unit | List the concerns one function handles. Report when unrelated responsibilities or hidden control flow impose a concrete maintenance cost; length and number of steps are investigation leads. Name the concerns. Prefer a data/type reframing or early guard clause where it clarifies the contract; extract a separate unit only when it owns distinct state, a combinatorial test seam, or a layer boundary. | P2 |
| S9 | K, T, W | Generic naming | Does the type already say what the name says, and do neighboring files use a domain word? `data`, `result`, `temp`, `value`, `item`, `info`, `handler`, `processX`, `handleX`, `doX`; a `get` prefix on a property-like method; test names such as "should work" that state no behavior. Framework-domain names (`FocusManager`, `EventHandler` in an event system) are not generic. | P3 |
| S10 | T | Fake or hollow test | If the code under test were broken in the obvious way, would this test fail? Asserts on the fake or mock rather than behavior; `expect(x, x)`; "does not throw" or "is not null" as the only assertion; an expected value computed by re-running production logic; a body with no assertion; happy path only where a failure mode is obvious; `.only` or unexplained `.skip` left in the suite. Also a coverage gap: a public entry point of the unit under test with an obvious failure path (a catch that releases and rethrows, a rejection branch) and no test at all, especially when the file wires up mocks for it and never asserts on them. | P2, P1 if it masks a real failure or leaves `.only` |
| S11 | K | Non-idiomatic implementation | Does a version-supported language/framework idiom prevent a concrete error or materially simplify the code? Verify the relevant primary guidance and local constraints; syntax preferences alone are not defects. | P2 |
| S12 | K, T, W | Dead ceremony | Unused private helpers; a lint suppression for a rule that is not enabled or no longer fires; obsolete or misleading TODOs; a utility duplicated from elsewhere in-tree; configuration knobs with one value; commented-out code; compatibility shims or "legacy" aliases in code that has no compatibility promise. | P2 |
| S13 | K, T | Architecture mismatch | Does the code cross a boundary the repository states? A UI layer calling native or IO directly; a reinvented framework primitive (focus, routing, hit testing, text editing) where one exists; a new test harness or fake that re-implements framework behavior instead of using the documented harnesses; a package importing another package's private modules. Derive the boundaries from the repository's own instructions; do not invent them. | P1 |
| S14 | C, W | Misleading documentation | Unsupported claims, obsolete API references, unfilled placeholders, or authoring residue. Repetition, emphasis, and typography are leads only; show an actual misleading statement, requirement violation, or maintenance cost. | P3 |
| S15 | K | Tangled responsibilities | Does this change create split ownership, unrelated responsibilities, or branching that a clearer data/state model would remove? File length is a lead, not a threshold violation. Explain the coupling and feasible decomposition. | P2 |
| S16 | C, K, W | Stray development artifact | Is this a temporary assistant note, debug dump, backup, or orphaned asset without a maintained purpose? Inspect build, test, glob discovery, docs, packaging, and repository policy. Keep legitimate fixtures, generators, benchmarks, and design records. Explain the cost or exposure and safe removal/relocation. | P3; raise for demonstrated impact |

Lens **T** also carries S1 and S3 for comments inside tests, S5 for catch-alls that swallow a test
failure, S9 for empty test names, S12 for dead ceremony in tests, and S13 for a new harness.
Lens **W** carries whatever its hit lists cover.

## Never report

- Duplicate mechanical style findings already covered by configured tooling. A demonstrated
  correctness defect remains reportable even if a tool can also detect it.
- The existence of a doc comment on a public member when the repository requires one. Judge content only.
- Any comment that explains **why**: ordering, invariants, encoding, ABI, a rejected alternative, a
  bounded leak, a backstop that is normally unreachable. First-person "we" inside a why-comment is fine.
- Numbered steps where each step states an ordering constraint.
- Test names that read as specifications, however long.
- Repetition that is the test's point (tables of cases, parameterized inputs).
- Emoji or unusual Unicode inside string literals; they are usually test data.
- A file solely because it is a golden, fixture, generated, or vendored file. Check its
  purpose, consumers, and provenance; those categories are not exempt from review.
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
  call sites, linter config). `medium`: could be house style. `low`: smell only; report an unresolved question or omit it. Agreement between finders
  does not increase the underlying evidence.

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

Use primary sources that actually support the finding for the project's versions. Cite the
specific rule or contract, and distinguish required semantics from recommendations. This
catalog is a set of investigation leads, not proof of authorship or a substitute for evidence.

## Building repo calibration

When calibration would resolve an uncertain boundary, use actual repository examples to
**report** with the pattern and fix and examples to **keep**
that a naive reader would flag (a why-comment, a justified backstop, numbered ordering steps, a
domain name that looks generic). Put them in the finder prompt. Over-reporting on S1 and S3 is the
known failure mode; keep examples help test the boundary. Do not manufacture findings or
examples to meet a quota.
