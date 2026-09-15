#!/usr/bin/env python3
"""Mechanical gate for finder and validator output.

  python3 check_findings.py --root <repo> --workspace <ws> <ws>/findings/C-A1.json [...]
  python3 check_findings.py --root <repo> --workspace <ws> --validation <ws>/validations/VC-1.json [...]
  python3 check_findings.py --root <repo> --no-slices [--diff-range main...HEAD] findings.json

Finder checks: JSON parses; every slice file appears in files_reviewed with
lines_read equal to its real line count (skipped with --no-slices); every
finding's pattern is in the agent's lens; severity and confidence are valid;
the first non-blank snippet line appears within one line of the cited range;
with --diff-range, every finding not marked "preexisting": true sits inside a
changed hunk. Validator checks: every input finding id has exactly one verdict
with a reason; downgrade and reclassify carry the new value; missed[] entries
pass the finder checks. Exit 1 when anything fails; one line per problem.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

LENS = {
    "C": {"S1", "S2", "S3", "S4", "S14"},
    "K": {"S5", "S6", "S7", "S8", "S9", "S11", "S12", "S13"},
    "T": {"S10", "S12", "S9", "S1", "S3", "S5", "S13"},
    "W": {"S1", "S2", "S3", "S4", "S5", "S9", "S12", "S14"},
}
SEVERITIES = {"P1", "P2", "P3"}
CONFIDENCES = {"high", "medium", "low"}
VERDICTS = {"confirm", "downgrade", "reject", "reclassify"}
MAX_SNIPPET_LINES = 4


def wc(path: Path) -> int:
    with open(path, "rb") as handle:
        return sum(1 for _ in handle)


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def changed_hunks(root: Path, diff_range: str) -> dict[str, list[tuple[int, int]]]:
    """Map path -> [(start, end)] of added/modified line ranges in the diff."""
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "-U0", "--no-color", diff_range],
        capture_output=True, text=True, check=True,
    )
    hunks: dict[str, list[tuple[int, int]]] = {}
    current = None
    for line in result.stdout.splitlines():
        if line.startswith("+++ "):
            target = line[4:].strip()
            current = None if target == "/dev/null" else target[2:] if target.startswith("b/") else target
        elif line.startswith("@@") and current is not None:
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                start = int(match.group(1))
                count = int(match.group(2)) if match.group(2) is not None else 1
                if count > 0:
                    hunks.setdefault(current, []).append((start, start + count - 1))
    return hunks


def check_finding(finding: dict, lens: str, root: Path, problems: list[str], where: str,
                  hunks: dict[str, list[tuple[int, int]]] | None) -> None:
    fid = finding.get("id", "?")
    if finding.get("pattern") not in LENS.get(lens, set()):
        problems.append(f"{where} {fid}: pattern {finding.get('pattern')} not in lens {lens}")
    if finding.get("severity") not in SEVERITIES:
        problems.append(f"{where} {fid}: bad severity {finding.get('severity')}")
    if finding.get("confidence") not in CONFIDENCES:
        problems.append(f"{where} {fid}: bad confidence {finding.get('confidence')}")
    rel = finding.get("path")
    start, end = finding.get("start_line"), finding.get("end_line")
    if not rel or not (root / rel).is_file():
        problems.append(f"{where} {fid}: path missing on disk: {rel}")
        return
    if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
        problems.append(f"{where} {fid}: bad line range {start}-{end}")
        return
    path = root / rel
    total = wc(path)
    if end > total:
        problems.append(f"{where} {fid}: end_line {end} > file length {total}")
        return
    snippet = [l for l in (finding.get("snippet") or "").split("\n") if l.strip()]
    if not snippet:
        problems.append(f"{where} {fid}: empty snippet")
        return
    if len(snippet) > MAX_SNIPPET_LINES:
        problems.append(f"{where} {fid}: snippet longer than {MAX_SNIPPET_LINES} lines")
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    window = lines[max(0, start - 2): min(total, end + 1)]
    probe = re.sub(r"\s+", " ", snippet[0]).strip()
    if not any(probe in re.sub(r"\s+", " ", w) for w in window):
        problems.append(f"{where} {fid}: snippet not found at {rel}:{start}-{end}: {probe[:80]!r}")
    if hunks is not None and not finding.get("preexisting"):
        ranges = hunks.get(rel, [])
        if not any(s <= end and start <= e for s, e in ranges):
            problems.append(f"{where} {fid}: outside the diff at {rel}:{start}-{end} (mark preexisting or drop)")


def check_finder(path: Path, root: Path, workspace: Path | None, problems: list[str],
                 hunks: dict[str, list[tuple[int, int]]] | None) -> tuple[str, int]:
    data = load_json(path)
    agent_id = data.get("agent_id", path.stem)
    lens = agent_id.split("-")[0]
    slice_id = agent_id.split("-", 1)[1] if "-" in agent_id else None
    reviewed = {r["path"]: r.get("lines_read") for r in data.get("files_reviewed", []) if isinstance(r, dict)}
    if workspace is not None and lens != "W":
        slice_file = workspace / "slices" / f"{slice_id}.txt"
        expected = set(slice_file.read_text(encoding="utf-8").split()) if slice_file.is_file() else set()
        if not expected:
            problems.append(f"{agent_id}: slice list not found or empty: {slice_file}")
        for missing in sorted(expected - set(reviewed)):
            problems.append(f"{agent_id}: not reviewed: {missing}")
    for rel, lines_read in reviewed.items():
        full = root / rel
        if full.is_file() and lines_read != wc(full):
            problems.append(f"{agent_id}: lines_read {lines_read} != {wc(full)} for {rel}")
    for finding in data.get("findings", []):
        check_finding(finding, lens, root, problems, agent_id, hunks)
    return agent_id, len(data.get("findings", []))


def check_validation(path: Path, root: Path, workspace: Path | None, problems: list[str],
                     hunks: dict[str, list[tuple[int, int]]] | None) -> tuple[str, dict[str, int]]:
    data = load_json(path)
    agent_id = data.get("agent_id", path.stem)
    expected: set[str] = set()
    for input_id in data.get("inputs", []):
        candidates = [workspace / "findings" / f"{input_id}.json"] if workspace else []
        candidates.append(path.parent / "input" / f"{input_id}.json")
        for candidate in candidates:
            if candidate.is_file():
                expected |= {x["id"] for x in load_json(candidate).get("findings", [])}
                break
        else:
            problems.append(f"{agent_id}: input findings not found for {input_id}")
    seen: list[str] = []
    for review in data.get("reviews", []):
        fid = review.get("finding_id")
        seen.append(fid)
        verdict = review.get("verdict")
        if verdict not in VERDICTS:
            problems.append(f"{agent_id} {fid}: bad verdict {verdict}")
        if not (review.get("reason") or "").strip():
            problems.append(f"{agent_id} {fid}: missing reason")
        if verdict == "downgrade" and review.get("severity") not in SEVERITIES:
            problems.append(f"{agent_id} {fid}: downgrade without a valid new severity")
        if verdict == "reclassify" and not review.get("pattern"):
            problems.append(f"{agent_id} {fid}: reclassify without a new pattern")
    for fid in sorted(expected - set(seen)):
        problems.append(f"{agent_id}: no verdict for {fid}")
    for fid in sorted({x for x in seen if seen.count(x) > 1}):
        problems.append(f"{agent_id}: duplicate verdict for {fid}")
    for finding in data.get("missed", []):
        check_finding(finding, finding.get("lens", "K"), root, problems, f"{agent_id} missed", hunks)
    counts: dict[str, int] = {}
    for review in data.get("reviews", []):
        counts[review.get("verdict")] = counts.get(review.get("verdict"), 0) + 1
    return agent_id, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", required=True, type=Path, help="repository root the cited paths are relative to")
    parser.add_argument("--workspace", type=Path, help="review workspace holding slices/ and findings/")
    parser.add_argument("--no-slices", action="store_true", help="skip the slice coverage check (inline reviews)")
    parser.add_argument("--validation", action="store_true", help="check validator output instead of finder output")
    parser.add_argument("--diff-range", help="git range; findings must sit inside its changed hunks unless marked preexisting")
    parser.add_argument("files", nargs="+", type=Path, help="JSON files to check")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    workspace = None if args.no_slices else (args.workspace.resolve() if args.workspace else None)
    if workspace is None and not args.no_slices and not args.validation:
        parser.error("--workspace is required unless --no-slices is given")
    hunks = changed_hunks(root, args.diff_range) if args.diff_range else None
    problems: list[str] = []
    for file in args.files:
        try:
            if args.validation:
                agent_id, counts = check_validation(file, root, workspace, problems, hunks)
                print(f"{agent_id}: {counts}")
            else:
                agent_id, n = check_finder(file, root, workspace, problems, hunks)
                print(f"{agent_id}: {n} findings")
        except Exception as error:  # a malformed file is a gate failure, not a crash
            problems.append(f"{file}: unreadable: {error}")
    for problem in problems:
        print("PROBLEM", problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
