#!/usr/bin/env python3
"""Shared scope helpers for the ai-slop-review scripts.

Gathers the in-scope files for a review, classifies each one by language
family and role (source, test, doc), and exposes the comment syntax the sweep
patterns need. Imported by slice.py, sweep.py, and check_findings.py.
"""
from __future__ import annotations

import fnmatch
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

# Languages whose line comments start with "//" and doc comments with "///" or "/**".
SLASH_LANGS = {
    "dart", "ts", "tsx", "js", "jsx", "mjs", "cjs", "go", "rs", "java", "kt",
    "kts", "swift", "c", "cc", "cpp", "h", "hpp", "cs", "scala", "php",
}
# Languages whose comments start with "#".
HASH_LANGS = {"py", "rb", "sh", "bash", "zsh", "pl", "r"}
DOC_LANGS = {"md", "mdx"}
CODE_LANGS = SLASH_LANGS | HASH_LANGS

# Languages where a "/* */" block used as documentation is a style violation
# (their doc convention is "///" or "//!"). JSDoc and Javadoc are excluded on
# purpose: "/** */" is the documented convention there.
BLOCK_DOC_IS_SLOP = {"dart", "rs", "cs", "go", "swift"}

DEFAULT_EXCLUDES = [
    ".git/*", "node_modules/*", "*/node_modules/*", "vendor/*", "*/vendor/*",
    "third_party/*", "*/third_party/*", "external/*", "*/external/*",
    "build/*", "*/build/*", "dist/*", "*/dist/*", "out/*", "*/out/*",
    "*.g.dart", "*.freezed.dart", "*.pb.dart", "*.pb.go", "*.pb.cc", "*.pb.h",
    "*.min.js", "*.min.css", "*.lock", "*.d.ts", "*/generated/*", "generated/*",
    "*.snap", "*.golden", "coverage/*", "*/coverage/*", "*.map",
]

TEST_DIR_NAMES = {"test", "tests", "spec", "specs", "__tests__", "testing", "integration_test"}
TEST_FILE_RE = re.compile(
    r"(^|/)(test_[^/]+\.py|[^/]+_test\.(dart|go|py|rs|cs|kt|java|swift|rb)|[^/]+\.(test|spec)\.[cm]?[jt]sx?|[^/]+_spec\.rb)$"
)


@dataclass(frozen=True)
class ScopeFile:
    path: str  # relative to root, posix separators
    lang: str
    role: str  # "source" | "test" | "doc"
    lines: int


def extension(path: str) -> str:
    return path.rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else ""


def is_excluded(path: str, excludes: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in excludes)


def is_test_path(path: str) -> bool:
    parts = path.split("/")
    if any(part in TEST_DIR_NAMES for part in parts[:-1]):
        return True
    return bool(TEST_FILE_RE.search(path))


def classify(path: str) -> tuple[str, str] | None:
    """Return (lang, role) for an in-scope path, or None when it is not reviewable."""
    ext = extension(path)
    if ext in DOC_LANGS:
        return ext, "doc"
    if ext in CODE_LANGS:
        return ext, "test" if is_test_path(path) else "source"
    return None


def count_lines(path: Path) -> int:
    with open(path, "rb") as handle:
        return sum(1 for _ in handle)


def list_tracked(root: Path) -> list[str]:
    """Tracked plus untracked-but-not-ignored paths under root.

    Falls back to a filesystem walk when git is unavailable or lists nothing,
    which happens when the root is not a repository or sits inside an ignored
    directory of one.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            capture_output=True, check=True,
        )
        listed = [p.decode("utf-8", "replace") for p in result.stdout.split(b"\0") if p]
        if listed:
            return listed
    except (OSError, subprocess.CalledProcessError):
        pass
    return sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and ".git" not in p.parts
    )


def read_file_list(list_path: Path) -> list[str]:
    return [line.strip() for line in list_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def gather(root: Path, files: list[str] | None = None, excludes: list[str] | None = None,
           include: list[str] | None = None) -> list[ScopeFile]:
    """Build the in-scope file set.

    `files` restricts the scope to an explicit list (for example, the changed
    files of a diff); otherwise every tracked file is considered. `include`
    keeps only paths matching at least one glob. Excludes always apply.
    """
    patterns = list(DEFAULT_EXCLUDES) + list(excludes or [])
    candidates = files if files is not None else list_tracked(root)
    scoped: list[ScopeFile] = []
    for raw in candidates:
        rel = raw.replace("\\", "/").lstrip("./")
        if include and not any(fnmatch.fnmatch(rel, g) for g in include):
            continue
        if is_excluded(rel, patterns):
            continue
        kind = classify(rel)
        if kind is None:
            continue
        full = root / rel
        if not full.is_file():
            continue
        lang, role = kind
        scoped.append(ScopeFile(rel, lang, role, count_lines(full)))
    return sorted(scoped, key=lambda f: f.path)


def comment_prefix(lang: str) -> str | None:
    """Regex for a line-comment opener in this language, or None for prose."""
    if lang in SLASH_LANGS:
        return r"//+"
    if lang in HASH_LANGS:
        return r"#+"
    return None
