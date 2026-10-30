#!/usr/bin/env python3
"""Cut the review scope into slices that one finder agent can read in full.

  python3 slice.py --root <repo> --out <workspace> [--files changed.txt]
                   [--budget 6000] [--test-budget 9000] [--doc-budget 9000]
                   [--include 'lib/*' ...] [--exclude 'website/*' ...]

Writes <workspace>/slices/<ID>.txt (one path per line), a MANIFEST.txt with
id, file count, line count, and lenses, and fails loudly when any in-scope
file is assigned to zero or two slices or does not exist. Source slices are
A1..An (lenses C and K), test slices T1..Tn (lens T), doc slices D1..Dn
(lens C). Files are path-sorted so a slice stays inside one area of the tree.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _scope import ScopeFile, gather, read_file_list  # noqa: E402

LENSES = {"A": "C,K", "T": "T", "D": "C"}


def cut(files: list[ScopeFile], prefix: str, budget: int) -> dict[str, list[ScopeFile]]:
    """Group path-sorted files into slices of roughly `budget` lines.

    A file never splits across slices; a single file larger than the budget
    becomes its own slice. The finder prompt handles chunked reads of long files.
    """
    slices: dict[str, list[ScopeFile]] = {}
    current: list[ScopeFile] = []
    acc = 0
    index = 1
    for f in files:
        if current and acc + f.lines > budget:
            slices[f"{prefix}{index}"] = current
            index += 1
            current, acc = [], 0
        current.append(f)
        acc += f.lines
    if current:
        slices[f"{prefix}{index}"] = current
    return slices


def build_slices(files: list[ScopeFile], budget: int, test_budget: int,
                 doc_budget: int) -> dict[str, list[ScopeFile]]:
    by_role = {"source": [], "test": [], "doc": []}
    for f in files:
        by_role[f.role].append(f)
    result: dict[str, list[ScopeFile]] = {}
    result.update(cut(by_role["source"], "A", budget))
    result.update(cut(by_role["test"], "T", test_budget))
    result.update(cut(by_role["doc"], "D", doc_budget))
    return result


def coverage_problems(files: list[ScopeFile], slices: dict[str, list[ScopeFile]],
                      root: Path) -> list[str]:
    assigned: dict[str, int] = {}
    for members in slices.values():
        for f in members:
            assigned[f.path] = assigned.get(f.path, 0) + 1
    problems = []
    for f in files:
        if f.path not in assigned:
            problems.append(f"unassigned: {f.path}")
        if not (root / f.path).is_file():
            problems.append(f"MISSING: {f.path}")
    for path, n in assigned.items():
        if n > 1:
            problems.append(f"duplicate: {path} in {n} slices")
    return problems


def write_slices(slices: dict[str, list[ScopeFile]], out: Path) -> Path:
    slices_dir = out / "slices"
    slices_dir.mkdir(parents=True, exist_ok=True)
    for old in slices_dir.glob("*.txt"):
        old.unlink()
    manifest = [f"{'id':<5}{'files':>6}{'lines':>8}  lenses"]
    for sid, members in slices.items():
        (slices_dir / f"{sid}.txt").write_text("".join(f"{f.path}\n" for f in members), encoding="utf-8")
        manifest.append(f"{sid:<5}{len(members):>6}{sum(f.lines for f in members):>8}  {LENSES[sid[0]]}")
    (slices_dir / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    return slices_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", required=True, type=Path, help="repository root")
    parser.add_argument("--out", required=True, type=Path, help="review workspace directory")
    parser.add_argument("--files", type=Path, help="explicit file list (paths relative to root), e.g. a diff's changed files")
    parser.add_argument("--include", action="append", default=[], help="glob to keep (repeatable)")
    parser.add_argument("--exclude", action="append", default=[], help="glob to drop (repeatable), added to the built-in excludes")
    parser.add_argument("--budget", type=int, default=6000, help="target lines per source slice")
    parser.add_argument("--test-budget", type=int, default=9000, help="target lines per test slice")
    parser.add_argument("--doc-budget", type=int, default=9000, help="target lines per doc slice")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    explicit = read_file_list(args.files) if args.files else None
    files = gather(root, explicit, args.exclude, args.include or None)
    if not files:
        print("no reviewable files in scope", file=sys.stderr)
        return 1
    slices = build_slices(files, args.budget, args.test_budget, args.doc_budget)
    slices_dir = write_slices(slices, args.out.resolve())
    print((slices_dir / "MANIFEST.txt").read_text(encoding="utf-8"), end="")
    problems = coverage_problems(files, slices, root)
    for problem in problems:
        print("PROBLEM", problem)
    print(f"{len(files)} files in {len(slices)} slices -> {slices_dir}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
