# Delegated orchestration

Use this reference for a large review that benefits from slicing, whether executed sequentially
or with permitted subagents. The skill's execution policy governs delegation; line counts are
planning estimates, not a requirement to spawn agents. For small reviews, the inline procedure
and the output contract below are sufficient.

## Contents

1. [Workspace layout](#1-workspace-layout)
2. [Slicing and lenses](#2-slicing-and-lenses)
3. [Waves](#3-waves)
4. [Output contracts](#4-output-contracts)
5. [Gate after every wave](#5-gate-after-every-wave)
6. [Validators](#6-validators)
7. [Merge, spot-check, report](#7-merge-spot-check-report)
8. [Stop conditions](#8-stop-conditions)

## 1. Workspace layout

Keep every artifact outside the repository so a read-only run leaves `git status` clean. A
temporary directory or a user-named directory is fine; a gitignored `.context/` inside the repo
also works when the user prefers it.

```
<workspace>/
  slices/<ID>.txt          from slice.py; one path per line, plus MANIFEST.txt
  sweep/*.txt              from sweep.py; hit lists, hints-<T-slice>.txt, SUMMARY.txt
  findings/<AGENT>.json    finder output
  validations/input/       finder output with `why`, `notes`, `hints_triaged` stripped
  validations/<AGENT>.json validator output
  REPORT.md                orchestrator synthesis
```

Preflight, from the repository root, with `<skill>` set to this skill's directory:

```bash
python3 <skill>/scripts/slice.py --root . --out <workspace>            # must report no PROBLEM lines
python3 <skill>/scripts/sweep.py --root . --out <workspace>            # regenerates sweep/ and prints SUMMARY
mkdir -p <workspace>/findings <workspace>/validations/input
git status --short                                                      # record and preserve pre-existing changes
```

Pass `--files changed.txt` to both scripts when the scope is a diff (`git diff --name-only
<range> > changed.txt`). Pass `--include` and `--exclude` globs to narrow a repository scope.

## 2. Slicing and lenses

`slice.py` cuts path-sorted files into slices one agent can read in full: source slices `A1..An`
at about 6,000 lines (comment-dense code reads slower), test slices `T1..Tn` at about 9,000 lines
(a simpler lens), doc slices `D1..Dn`. Adjust with `--budget`, `--test-budget`, `--doc-budget`.
A file never splits across slices; the finder prompt handles chunked reads of long files.

One lens per agent. Agent id is `<LENS>-<SLICE>`:

| Lens | Runs on | Patterns |
|---|---|---|
| C | every A and D slice | S1, S2, S3, S4, S14 |
| K | every A slice | S5, S6, S7, S8, S9, S11, S12, S13 |
| T | every T slice | S10, plus S1, S3, S5, S9, S12, S13 inside tests |
| W | the sweep hit lists, once | whatever the hit lists cover |

Count: `W` + `C × (A + D)` + `K × A` + `T × T` finders. A 60,000-line repository lands near 35.

## 3. Waves

Run slices sequentially by default. If delegation is permitted, choose a bounded wave that fits
the available slots and the user's cost/model preferences; no fixed agent count is required.
Wait for the wave to finish and run the gate before continuing. Run
`W-1` in the first wave; its findings aggregate repo-wide patterns that per-slice finders would
report sixty times.

Each finder prompt is self-contained: rules for its lens, the never-report list, repo facts,
calibration examples, the reading protocol, and the output contract. Compose it from
`prompts.md`; the finder never opens the rubric or this file.

## 4. Output contracts

Finder → `<workspace>/findings/<AGENT_ID>.json`:

```json
{
  "agent_id": "C-A3",
  "files_reviewed": [ { "path": "lib/widgets/row.dart", "lines_read": 162 } ],
  "files_skipped": [],
  "hints_triaged": [],
  "notes": "",
  "findings": [
    {
      "id": "C-A3-001",
      "path": "lib/widgets/row.dart",
      "start_line": 136,
      "end_line": 136,
      "pattern": "S1",
      "severity": "P3",
      "confidence": "high",
      "snippet": "/// This widget uses RenderFlex for proper flex layout.",
      "guideline": "Effective Dart Documentation: AVOID redundancy with the surrounding context",
      "why": "Names the implementation type with filler; the summary line above already says what the widget is.",
      "fix": "Delete the sentence."
    }
  ]
}
```

`files_reviewed` lists every slice file with `lines_read` equal to its real line count; a
partial read is visible and the gate sends it back. `hints_triaged` is required for T and W
agents: one entry per hint, `{"hint": "path:line", "outcome": "reported" | "not_slop",
"finding_id": "..." | null, "reason": "..."}`. A finding inside a diff-scoped review that
points at untouched code carries `"preexisting": true`.

Validator → `<workspace>/validations/<AGENT_ID>.json`:

```json
{
  "agent_id": "VC-1",
  "inputs": ["C-A1", "C-A2", "C-A3"],
  "reviews": [
    { "finding_id": "C-A1-001", "verdict": "confirm", "severity": "P3", "confidence": "high",
      "reason": "Line 42 reads `// increment the counter` directly above `_count++`." },
    { "finding_id": "C-A1-002", "verdict": "reject",
      "reason": "Lines 88-90 explain why the branch is unreachable after unmount; that is a why-comment." }
  ],
  "missed": []
}
```

Every input finding id gets exactly one verdict. `reason` quotes or paraphrases the code at the
cited lines; a reason that could apply to any finding is not a reason. `missed` may add P1 or P2
findings only, only in files that appear in the inputs, using the finder schema plus `"lens"`.

## 5. Gate after every wave

```bash
python3 <skill>/scripts/check_findings.py --root . --workspace <workspace> <workspace>/findings/<the five>.json
git status --short   # any tracked change means an agent edited; revert it and discard that agent's output
```

The gate checks that JSON parses, every slice file was read to its last line, every pattern is in
the agent's lens, severity and confidence are valid, and the first snippet line exists within one
line of the cited range. Re-run only an agent the gate rejects, with the same prompt, once. If it
fails again, stop and report; the prompt or model needs changing, not more retries.

For validators:

```bash
python3 <skill>/scripts/check_findings.py --root . --workspace <workspace> --validation <workspace>/validations/<the five>.json
```

## 6. Validators

Build the blind inputs after all finder waves pass the gate:

```bash
for f in <workspace>/findings/*.json; do
  jq '{agent_id, findings: [.findings[] | {id,path,start_line,end_line,pattern,severity,confidence,snippet,guideline,fix}]}' \
    "$f" > "<workspace>/validations/input/$(basename "$f")"
done
jq -r '"\(.agent_id): \(.findings|length)"' <workspace>/findings/*.json   # re-pair if any exceeds ~60
```

Pair about three finders of the same lens per validator (`VC-n`, `VK-n`, `VT-n`; `W-1` gets its
own K-lens validator). A finder with more than about sixty findings gets its own validator. The
validator sees structured fields only, never the finder's `why`, and is told its job is to
disprove. Validator waves run after all finder waves.

Check whether verdicts address actual counterevidence. There is no required rejection or
downgrade percentage. Repeat only a pass with an identified evidence or reasoning defect.

## 7. Merge, spot-check, report

```bash
jq -s '[.[] | .reviews[]] | group_by(.verdict) | map({verdict: .[0].verdict, n: length})' <workspace>/validations/V*.json
```

Before writing a large report, spot-check material confirmed findings, emphasizing high-impact
and uncertain cases. Investigate disagreements against the actual evidence; a percentage alone
does not establish reviewer bias. Scale the sample to the report size.

`REPORT.md` contains:

- proposed, confirmed, downgraded, rejected, reclassified: per lens, per finder, per pattern
- every confirmed P1 and P2 with path, lines, snippet, and fix
- P3 clustered by file with counts; single P3s stay in the JSON
- ten sample rejections with reasons, so the reader can judge the validators
- validators with a reject rate under 15 percent, flagged
- files with zero findings across both lenses
- the spot-check result
- files not fully read and why

The user-facing summary leads with P1s, then P2s by file, then the P3 cluster list. No code edits
in this phase.

## 8. Stop conditions

- Two or more malformed outputs in one wave after a retry: stop and report.
- Any agent modifies a tracked file: `git checkout -- <file>`, discard that agent's output, note it.
- A finder reports fewer `lines_read` than a file's length twice in a row: split that slice and
  re-run.
- A validator wave rejects nothing after the strengthened re-run: report the finder output as
  unvalidated rather than as confirmed.
