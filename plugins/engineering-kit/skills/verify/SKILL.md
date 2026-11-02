---
name: verify
description: >
  Use when proving or disproving a specific technical claim, bug fix, UI/API behavior change, or
  performance/memory improvement with fresh falsifiable baseline-versus-treatment runtime evidence
  and returning a `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE` verdict. Do not use for vague
  stylistic claims or static code review without runtime measurement (use `wild-code-review`).
---

# Verify

Prove or disprove a concrete technical claim at runtime by capturing a reproducible **baseline (before)** measurement and comparing it against a **treatment (after)** measurement under identical conditions. Verification is not a summary of edits or a static code review—it tests whether the claimed fix or improvement actually holds when executed.

## When To Use

- The user asks "verify this", "prove it works", "did this fix it", or "show me the evidence".
- A bug fix needs a before/after reproduction showing the failure before the change and the pass after.
- A UI, CLI, API, performance, or memory claim needs real runtime measurement.
- Unit tests pass, but the real end-to-end or user-visible behavior still needs confirmation.

Do not use this for vague claims like "the code is cleaner". Ask for a measurable claim first, or use `wild-code-review` for static review.

## Workflow

1. Restate the claim in falsifiable form: condition, metric, and threshold.
2. Pick the smallest local surface that can disprove it.
3. Capture a baseline from the old state: merge base, parent commit, failing branch, or current broken repro.
4. Capture treatment from the changed state with the same command, data, warmup, and environment.
5. Compare raw artifacts: numbers, screenshots, terminal transcripts, HTTP responses, profiles, heap snapshots, or test output.
6. Return exactly one verdict: `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`.

## Local Surfaces

- Code behavior: focused unit/integration tests or a minimal repro script.
- CLI/TUI behavior: terminal transcript, isolated PTY/`tmux` harness, or demo recording.
- UI behavior: native host browser or Playwright tooling, screenshots, accessibility snapshots, or browser traces.
- API behavior: local HTTP/RPC request and response diff.
- Performance: same-machine baseline/treatment timings or CPU profiles.
- Memory: heap snapshots before and after the suspected operation.

## Artifact Layout

When safe to write artifacts:

```text
/tmp/verify/<claim-slug>/
├── claim.md
├── timeline.md
├── baseline/
├── treatment/
├── diff/
└── verdict.md
```

If artifacts may contain sensitive code, prompts, screenshots, HTTP bodies, or heap data, keep only the minimal inline evidence unless the user agrees to disk storage.

## Verdict Rules

- `VERIFIED`: baseline and treatment differ in the predicted direction, by the claimed threshold, with no obvious confound.
- `NOT VERIFIED`: the behavior is unchanged, moves the wrong way, or misses the threshold.
- `INCONCLUSIVE`: no valid baseline, noisy signal, failed measurement, or an environment difference invalidates the comparison.

## Output

Use this shape:

```text
VERIFIED | NOT VERIFIED | INCONCLUSIVE
Claim: <falsifiable claim>

Evidence:
<metric/artifact>: baseline=<...>, treatment=<...>, delta=<...>, threshold=<...>

Reasoning:
<one tight paragraph naming the evidence and any confounds>
```

Do not soften a negative result. A clear `NOT VERIFIED` is useful.
