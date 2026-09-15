#!/usr/bin/env python3
"""Pre-compute mechanical hit lists for the sweep agent and test-lens hints.

  python3 sweep.py --root <repo> --out <workspace> [--files changed.txt]
                   [--include GLOB ...] [--exclude GLOB ...]

Writes <workspace>/sweep/<rubric-id>-<pattern>.txt (one hit per line as
`path:line: text`), per-slice test hints (hints-<T-slice>.txt when
<workspace>/slices exists, otherwise one hints-ALL.txt), and SUMMARY.txt with
counts. Hits are leads for an agent to judge against the rubric, never
findings by themselves. Mechanical first, judgment second: an agent that
receives the hit list cannot miss a pattern and does not have to construct
greps.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _scope import (  # noqa: E402
    BLOCK_DOC_IS_SLOP, HASH_LANGS, SLASH_LANGS, ScopeFile, comment_prefix, gather, read_file_list,
)

CHAT_WORDS = (
    r"[Ss]imply|[Bb]asically|[Ee]ssentially|[Mm]ake sure|[Rr]obust|[Cc]omprehensive|"
    r"[Ss]eamless(ly)?|[Pp]roper(ly)?|[Ii]t'?s (important|worth) (to|noting)|[Ll]et'?s "
)
HISTORY_WORDS = r"previously|no longer|now uses|was changed|used to be|has been (updated|changed|moved|refactored)"
DOC_OPENER = r"(///|//!|/\*\*|\*|#|\"\"\"|''')"


def comment_patterns(lang: str) -> dict[str, re.Pattern[str]]:
    """Rubric-tagged regexes for one language's comment syntax."""
    c = comment_prefix(lang)
    if c is None:
        return {}
    return {
        "S1-S3-step-narration": re.compile(rf"{c}\s*(Step )?[0-9]+[.):]\s"),
        "S3-section-dividers": re.compile(rf"{c}\s*[-=*#]{{4,}}"),
        "S3-chat-voice": re.compile(rf"{c}.*\b(Note|NOTE|Important|IMPORTANT):|{c}\s.*\b({CHAT_WORDS})\b"),
        "S2-history-narration": re.compile(rf"{c}.*\b({HISTORY_WORDS})\b"),
        "S12-todo": re.compile(rf"{c}.*\b(TODO|FIXME|HACK|XXX)\b"),
        "S1-this-class-docs": re.compile(
            rf"{DOC_OPENER}\s*This (class|method|function|widget|getter|mixin|field|property|callback|"
            rf"enum|module|component|hook|service|struct|trait|interface|type)\b|{c}.*\bresponsible for\b"
        ),
        "S4-tag-style-docs": re.compile(
            rf"{DOC_OPENER}.*(@param\b|@returns?\b|@throws\b)|^\s*{DOC_OPENER}\s*(Args|Returns|Raises|Params?|Parameters):"
        ),
    }


LANG_PATTERNS: dict[str, dict[str, str]] = {
    # S5: catch-all handlers. Every hit must be opened; only swallowing handlers are findings.
    "S5-catch-all": {
        "dart": r"on Object catch|\}\s*catch\s*\(|catch \(_\)\s*\{\s*\}",
        "ts": r"\}\s*catch\s*(\(\s*\w*\s*\))?\s*\{", "tsx": r"\}\s*catch\s*(\(\s*\w*\s*\))?\s*\{",
        "js": r"\}\s*catch\s*(\(\s*\w*\s*\))?\s*\{", "jsx": r"\}\s*catch\s*(\(\s*\w*\s*\))?\s*\{",
        "mjs": r"\}\s*catch\s*(\(\s*\w*\s*\))?\s*\{", "cjs": r"\}\s*catch\s*(\(\s*\w*\s*\))?\s*\{",
        "py": r"^\s*except\s*(:|\(?\s*(Exception|BaseException)\b)",
        "java": r"catch\s*\(\s*(Exception|Throwable|RuntimeException)\b",
        "kt": r"catch\s*\(\s*\w+\s*:\s*(Exception|Throwable)\b",
        "cs": r"catch\s*(\(\s*(Exception|System\.Exception)\b|\{)",
        "swift": r"\}\s*catch\s*\{",
        "go": r"\brecover\(\)|^\s*_\s*=\s*err\b|,\s*_\s*(:=|=)\s*[\w.]+\(",
        "rs": r"\.unwrap_or_default\(\)|let _ = .*\?;|\.ok\(\);",
        "rb": r"^\s*rescue\s*(=>\s*\w+)?\s*$|rescue (StandardError|Exception)\b",
    },
    # S12: lint suppressions. The stale check below tells enabled from unknown for Dart.
    "S12-suppressions": {
        "dart": r"//\s*ignore(_for_file)?:\s*[a-z_, ]+",
        "ts": r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck", "tsx": r"eslint-disable|@ts-ignore|@ts-expect-error|@ts-nocheck",
        "js": r"eslint-disable", "jsx": r"eslint-disable", "mjs": r"eslint-disable", "cjs": r"eslint-disable",
        "py": r"#\s*(noqa|type:\s*ignore|pylint:\s*disable|nosec|pragma:\s*no cover)\b",
        "java": r"@SuppressWarnings\(", "kt": r"@Suppress\(", "cs": r"#pragma warning disable",
        "go": r"//\s*nolint\b", "rs": r"#!?\[allow\(", "swift": r"//\s*swiftlint:disable",
        "rb": r"#\s*rubocop:disable",
    },
    # S12: commented-out code. Statement-looking lines behind a comment marker.
    "S12-commented-out-code": {
        "_slash": r"^\s*//\s*(final|var|let|const|return|if \(|await |print\(|console\.|expect\(|import |[A-Za-z_][\w.]*\([^)]*\);\s*$)",
        "_hash": r"^\s*#\s*(return\b|if .*:\s*$|import |from .* import |print\(|self\.|def |[A-Za-z_][\w.]*\([^)]*\)\s*$)",
    },
    "S12-legacy-compat": {
        "_all": r"\b[Ll]egacy\b|[Bb]ackwards? ?compat|@[Dd]eprecated\b|\bshim\b|\bfor compatibility\b",
    },
    "S9-helper-manager-names": {
        "_slash": r"\b(class|final|var|let|const|void|interface|struct|type|[A-Z][A-Za-z]*)\s+[A-Za-z_]*(Helper|Manager|Util|Utils|Handler|Processor|Service)\b",
        "_hash": r"\b(class|def)\s+[A-Za-z_]*(Helper|Manager|Util|Utils|Handler|Processor)\b",
    },
}

EMOJI = re.compile("[\U0001F300-\U0001FAFF✅❌⚠✨⭐✔]")
BLOCK_DOC = re.compile(r"^\s*/\*(?!\*/)")

TEST_PATTERNS = {
    "S9-S10-marketing-test-name": r"(\b(test|it|testWidgets|describe)\(\s*['\"`][^'\"`]*|def test_\w*|func Test\w*)(should work|correctly|properly|as expected|works|_works|_correctly|_properly)\b",
    "S10-arrange-act-assert": r"(//|#)\s*(Arrange|Act|Assert|Given|When|Then)\b",
    "S10-returns-normally-only": r"returnsNormally|not\.toThrow\(\)|assertDoesNotThrow|does_not_raise|assert_not_raises",
    "S10-tautology": r"expect\(\s*(true|false)\s*,\s*is(True|False)\s*\)|expect\((\w+),\s*\3\)|expect\((\w+)\)\.toBe\(\4\)|assertEqual\((\w+),\s*\5\)|assert (\w+) == \6\b",
    "S10-only-not-null": r"expect\([^,]+,\s*isNotNull\s*\)|\.toBeDefined\(\)|\.toBeTruthy\(\)|assertIsNotNone\(|assert \w+ is not None\s*$",
    # Expected side computed from the input (a reduce/map/sum over the same data) instead of a literal.
    "S10-computed-expected": r"\.(toBe|toEqual|toStrictEqual)\([^;]*\.(reduce|map|filter|fold|sum)\(|expect\([^,]+,\s*[^;]*\.(reduce|map|fold)\(|assert(Equal|Eq)\([^,]+,\s*[^;]*\.(reduce|map|sum)\(|\bsum\([^)]*\)\s*\)\s*$",
    "S12-test-suppression": r"//\s*ignore_for_file:|eslint-disable|#\s*noqa|@ts-ignore",
}
TEST_DECL = re.compile(r"\b(test|it|testWidgets)\(|^\s*def test_\w+|^\s*func Test\w+|#\[test\]|@Test\b|^\s*it\s+['\"]", re.M)
EXPECT_CALL = re.compile(
    r"\bexpect(Later)?\(|\bassert(Equal|True|False|In|Is|Raises|That|Eq|_eq!|_ne!|!)?\b|\bt\.(Error|Fatal|Errorf|Fatalf)\b|\brequire\.|\bassert\.|\bshould\.|\bverify\("
)

# Analyzer diagnostic names that are legitimately suppressed even though no lint list enables them.
DART_DIAGNOSTICS = {
    "unused_element", "unused_field", "unused_import", "unused_local_variable", "deprecated_member_use",
    "deprecated_member_use_from_same_package", "invalid_use_of_internal_member",
    "invalid_use_of_visible_for_testing_member", "invalid_use_of_protected_member", "undefined_hidden_name",
    "implementation_imports", "todo", "dead_code", "unreachable_from_main", "avoid_print",
}


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def lang_regex(name: str, lang: str) -> re.Pattern[str] | None:
    table = LANG_PATTERNS[name]
    raw = table.get(lang)
    if raw is None and lang in SLASH_LANGS:
        raw = table.get("_slash")
    if raw is None and lang in HASH_LANGS:
        raw = table.get("_hash")
    if raw is None:
        raw = table.get("_all")
    return re.compile(raw) if raw else None


def hit(path: str, lineno: int, text: str, tag: str | None = None) -> str:
    label = f" [{tag}]" if tag else ""
    return f"{path}:{lineno}:{label} {text.rstrip()[:160]}"


def sweep_code(files: list[ScopeFile], root: Path) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = defaultdict(list)
    for f in files:
        lines = read_lines(root / f.path)
        if f.role == "doc":
            for i, line in enumerate(lines, 1):
                if EMOJI.search(line):
                    hits["S3-S14-emoji"].append(hit(f.path, i, line))
            continue
        per_lang = comment_patterns(f.lang)
        multi = {name: lang_regex(name, f.lang) for name in LANG_PATTERNS}
        for i, line in enumerate(lines, 1):
            for name, rx in per_lang.items():
                if rx.search(line):
                    hits[name].append(hit(f.path, i, line))
            for name, rx in multi.items():
                if rx and rx.search(line):
                    hits[name].append(hit(f.path, i, line))
            if f.lang in BLOCK_DOC_IS_SLOP and BLOCK_DOC.search(line):
                hits["S3-block-comment-docs"].append(hit(f.path, i, line))
            if EMOJI.search(line):
                hits["S3-S14-emoji"].append(hit(f.path, i, line))
    return hits


def enabled_dart_lints(root: Path) -> set[str] | None:
    """Lint names enabled by analysis_options.yaml plus package:lints, or None when absent."""
    options = root / "analysis_options.yaml"
    if not options.is_file():
        return None

    def rules_from(text: str) -> set[str]:
        return set(re.findall(r"^\s+([a-z_]+):\s*true\s*$", text, re.M)) | set(
            re.findall(r"^\s+-\s+([a-z_]+)\s*$", text, re.M)
        )

    text = options.read_text(encoding="utf-8", errors="replace")
    enabled = rules_from(text)
    lock = root / "pubspec.lock"
    if "package:lints" in text and lock.is_file():
        match = re.search(r'\n  lints:\n(?:.*\n){1,6}?\s+version: "?([0-9.]+)', lock.read_text(encoding="utf-8", errors="replace"))
        if match:
            base = Path.home() / ".pub-cache/hosted/pub.dev" / f"lints-{match.group(1)}" / "lib"
            for yml in ("core.yaml", "recommended.yaml"):
                if (base / yml).is_file():
                    enabled |= rules_from((base / yml).read_text(encoding="utf-8", errors="replace"))
    return enabled


def stale_dart_suppressions(suppression_hits: list[str], enabled: set[str]) -> dict[str, list[str]]:
    stale: dict[str, set[str]] = defaultdict(set)
    for line in suppression_hits:
        if "ignore" not in line:
            continue
        match = re.search(r"ignore(?:_for_file)?:\s*([a-z_, ]+)", line)
        if not match:
            continue
        for lint in (x.strip() for x in match.group(1).split(",")):
            if lint and lint not in enabled and lint not in DART_DIAGNOSTICS:
                stale[lint].add(line.split(":")[0])
    return {lint: sorted(paths) for lint, paths in stale.items()}


def test_hints(files: list[ScopeFile], root: Path) -> dict[str, list[str]]:
    hints: dict[str, list[str]] = defaultdict(list)
    compiled = {name: re.compile(rx) for name, rx in TEST_PATTERNS.items()}
    for f in files:
        if f.role != "test":
            continue
        lines = read_lines(root / f.path)
        for i, line in enumerate(lines, 1):
            for name, rx in compiled.items():
                if rx.search(line):
                    hints[f.path].append(hit(f.path, i, line, name))
        src = "\n".join(lines)
        n_tests = len(TEST_DECL.findall(src))
        n_expects = len(EXPECT_CALL.findall(src))
        if n_tests and n_expects == 0:
            hints[f.path].append(hit(f.path, 1, f"{n_tests} test bodies, 0 assertions", "S10-no-expect"))
        elif n_tests and n_expects < n_tests:
            hints[f.path].append(hit(f.path, 1, f"{n_tests} test bodies, {n_expects} assertions", "S10-few-expects"))
    return hints


def write_outputs(out: Path, hits: dict[str, list[str]], hints: dict[str, list[str]],
                  stale: dict[str, list[str]] | None, enabled_count: int | None) -> Path:
    sweep_dir = out / "sweep"
    sweep_dir.mkdir(parents=True, exist_ok=True)
    for old in sweep_dir.glob("*.txt"):
        old.unlink()
    counts: dict[str, int] = {}
    for name in sorted(hits):
        (sweep_dir / f"{name}.txt").write_text("".join(f"{h}\n" for h in hits[name]), encoding="utf-8")
        counts[name] = len(hits[name])
    if stale is not None:
        with open(sweep_dir / "S12-stale-suppressions.txt", "w", encoding="utf-8") as handle:
            handle.write(f"# lints named in // ignore comments that no analysis_options.yaml or package:lints list enables ({enabled_count} enabled lints checked)\n")
            for lint, paths in sorted(stale.items(), key=lambda kv: -len(kv[1])):
                handle.write(f"\n{lint}: {len(paths)} files\n")
                handle.writelines(f"  {p}\n" for p in paths)
        counts["S12-stale-suppressions"] = sum(len(v) for v in stale.values())
    slices_dir = out / "slices"
    test_slices = sorted(slices_dir.glob("T*.txt")) if slices_dir.is_dir() else []
    if test_slices:
        for slice_file in test_slices:
            members = set(read_file_list(slice_file))
            lines = [h for p in sorted(members) for h in hints.get(p, [])]
            (sweep_dir / f"hints-{slice_file.stem}.txt").write_text("".join(f"{h}\n" for h in lines), encoding="utf-8")
            counts[f"hints-{slice_file.stem}"] = len(lines)
    else:
        lines = [h for p in sorted(hints) for h in hints[p]]
        (sweep_dir / "hints-ALL.txt").write_text("".join(f"{h}\n" for h in lines), encoding="utf-8")
        counts["hints-ALL"] = len(lines)
    summary = "".join(f"{v:6d}  {k}\n" for k, v in counts.items())
    (sweep_dir / "SUMMARY.txt").write_text(summary, encoding="utf-8")
    return sweep_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", required=True, type=Path, help="repository root")
    parser.add_argument("--out", required=True, type=Path, help="review workspace directory")
    parser.add_argument("--files", type=Path, help="explicit file list (paths relative to root)")
    parser.add_argument("--include", action="append", default=[], help="glob to keep (repeatable)")
    parser.add_argument("--exclude", action="append", default=[], help="glob to drop (repeatable)")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    explicit = read_file_list(args.files) if args.files else None
    files = gather(root, explicit, args.exclude, args.include or None)
    if not files:
        print("no reviewable files in scope", file=sys.stderr)
        return 1
    hits = sweep_code(files, root)
    enabled = enabled_dart_lints(root) if any(f.lang == "dart" for f in files) else None
    stale = stale_dart_suppressions(hits.get("S12-suppressions", []), enabled) if enabled is not None else None
    sweep_dir = write_outputs(args.out.resolve(), hits, test_hints(files, root), stale,
                              len(enabled) if enabled is not None else None)
    print((sweep_dir / "SUMMARY.txt").read_text(encoding="utf-8"), end="")
    print(f"-> {sweep_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
