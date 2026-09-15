#!/usr/bin/env python3
"""
Renumber SBVR rules sequentially within each rule category.

When you edit an SBVR specification — adding rules, removing rules, or
reorganizing them — the rule numbers can drift out of order. This script
walks the spec, groups rules by category prefix (D, B, DR, ST, etc.), and
re-issues sequential numbers per category in the order the rules appear in
the document.

It also rewrites cross-references inside other rule statements that point
to renumbered rules, so a rule like "see B3" stays correct after the
renumber.

Usage:
    python3 /path/to/renumber.py path/to/spec.md
    python3 /path/to/renumber.py path/to/spec.md --dry-run
    python3 /path/to/renumber.py path/to/spec.md --output path/to/new-spec.md

The script supports the narrative markdown format produced by the sbvr
skill, where rules look like:

    **D1:** It is necessary that ...
    **B2:** It is obligatory that ...
    **DR1:** average rating = ...

It does NOT touch fact type or term names. Only rule IDs.

For YAML output (output-formats.md), do not use this script — IDs in YAML
are referenced by other entries' `references` fields and a naive rewrite
would break those edges. Renumber YAML by hand or with a YAML-aware tool.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

# Match a rule heading at the start of a narrative rule line.
# Examples it catches:
#   **D1:** It is necessary that ...
#   **B12:** It is obligatory that ...
#   **DR3:** total = sum(...)
#   **ST1:** ...
RULE_HEADING = re.compile(r"^\s*(?:[-*+]\s+)?\*\*([A-Z]{1,3})(\d+):\*\*")

# Match an inline reference to a rule (used for cross-references like
# "see B3" or "(per D2)"). We require a word boundary so we don't catch
# things like "B12" inside a longer identifier.
RULE_REFERENCE = re.compile(r"\b([A-Z]{1,3})(\d+)\b")
INLINE_CODE_SPAN = re.compile(r"(`+).*?\1")
AUTOLINK = re.compile(r"<(?:https?://|mailto:)[^>\n]*>", re.IGNORECASE)
BARE_URI = re.compile(r"(?:https?://|mailto:)[^\s<>]+", re.IGNORECASE)
REFERENCE_DEFINITION = re.compile(
    r"^[ \t]{0,3}\[[^\]\n]+\]:[ \t]*(?P<destination><[^>\n]*>|\S+)"
)
TERMINAL_CONTROL_RE = re.compile(
    r"[\x00-\x1f\x7f-\x9f\u061c\u200e-\u200f\u202a-\u202e\u2066-\u2069]"
)


def markdown_prose_lines(text: str) -> list[tuple[str, bool]]:
    """Return lines with a flag that identifies content outside fenced code."""
    result: list[tuple[str, bool]] = []
    fence_character = ""
    fence_length = 0

    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        match = re.match(r"(`{3,}|~{3,})", stripped)
        if match and not fence_character:
            marker = match.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            result.append((line, False))
            continue
        if match and fence_character and match.group(1)[0] == fence_character \
                and len(match.group(1)) >= fence_length:
            result.append((line, False))
            fence_character = ""
            fence_length = 0
            continue
        result.append((line, not fence_character))

    return result


def replace_prose_references(line: str, mapping: dict[str, str]) -> str:
    """Rewrite rule IDs outside code spans and Markdown destinations."""
    def replace_segment(segment: str) -> str:
        def replace(match: re.Match[str]) -> str:
            old = f"{match.group(1)}{match.group(2)}"
            return mapping.get(old, old)

        return RULE_REFERENCE.sub(replace, segment)

    protected: list[tuple[int, int]] = [
        match.span() for match in INLINE_CODE_SPAN.finditer(line)
    ]
    protected.extend(match.span() for match in AUTOLINK.finditer(line))
    protected.extend(match.span() for match in BARE_URI.finditer(line))

    reference_definition = REFERENCE_DEFINITION.match(line)
    if reference_definition:
        protected.append(reference_definition.span("destination"))

    for match in re.finditer(r"\]\(", line):
        start = match.end() - 1
        depth = 0
        escaped = False
        for position in range(start, len(line)):
            character = line[position]
            if escaped:
                escaped = False
                continue
            if character == "\\":
                escaped = True
                continue
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0:
                    protected.append((start, position + 1))
                    break

    merged: list[tuple[int, int]] = []
    for start, end in sorted(protected):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    output: list[str] = []
    cursor = 0
    for start, end in merged:
        output.append(replace_segment(line[cursor:start]))
        output.append(line[start:end])
        cursor = end
    output.append(replace_segment(line[cursor:]))
    return "".join(output)


def renumber(text: str) -> tuple[str, dict[str, str]]:
    """
    Renumber rules in `text`. Returns the new text plus a mapping from
    old rule IDs to new rule IDs (e.g. {"B5": "B3"}).

    Rules are grouped by their letter prefix and renumbered in the order
    they first appear in the document.
    """
    # First pass: scan for rule headings in document order, build the
    # old-to-new map per category.
    counters: dict[str, int] = {}
    mapping: dict[str, str] = {}

    for line, is_prose in markdown_prose_lines(text):
        if not is_prose:
            continue
        match = RULE_HEADING.match(line)
        if match is None:
            continue
        prefix, number = match.group(1), match.group(2)
        old_id = f"{prefix}{number}"
        if old_id in mapping:
            raise ValueError(f"duplicate rule heading: {old_id}")
        counters[prefix] = counters.get(prefix, 0) + 1
        new_id = f"{prefix}{counters[prefix]}"
        mapping[old_id] = new_id

    if not mapping:
        return text, {}

    rewritten: list[str] = []
    for line, is_prose in markdown_prose_lines(text):
        rewritten.append(replace_prose_references(line, mapping) if is_prose else line)
    text = "".join(rewritten)

    return text, mapping


def terminal_text(value: object) -> str:
    """Render terminal-control characters as visible Unicode escapes."""
    return TERMINAL_CONTROL_RE.sub(
        lambda match: f"\\u{ord(match.group(0)):04x}", str(value)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to the SBVR markdown spec")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the rename map without modifying any file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write to this path instead of editing in place",
    )
    args = parser.parse_args()

    if args.path.is_symlink():
        print(
            f"error: refusing symlinked input: {terminal_text(args.path)}",
            file=sys.stderr,
        )
        return 1
    if not args.path.is_file():
        print(f"error: {terminal_text(args.path)} is not a file", file=sys.stderr)
        return 1
    if args.path.suffix.lower() != ".md":
        print(
            f"error: expected a Markdown file: {terminal_text(args.path)}",
            file=sys.stderr,
        )
        return 1

    try:
        original = args.path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(
            f"error: cannot read {terminal_text(args.path)}: {terminal_text(exc)}",
            file=sys.stderr,
        )
        return 1
    try:
        new_text, mapping = renumber(original)
    except ValueError as exc:
        print(f"error: {terminal_text(exc)}", file=sys.stderr)
        return 1

    if not mapping:
        print("No rules found. Nothing to renumber.")
        return 0

    changed = {old: new for old, new in mapping.items() if old != new}
    if not changed:
        print("All rules are already numbered sequentially. No changes made.")
        return 0

    print(f"Found {len(mapping)} rules. {len(changed)} will be renumbered:")
    for old, new in sorted(changed.items()):
        print(f"  {old} -> {new}")

    if args.dry_run:
        print("\n(dry run, no files written)")
        return 0

    target = args.output or args.path
    if target.is_symlink():
        print(
            f"error: refusing symlinked output: {terminal_text(target)}",
            file=sys.stderr,
        )
        return 1
    if target.exists() and not target.is_file():
        print(
            f"error: output is not a file: {terminal_text(target)}",
            file=sys.stderr,
        )
        return 1
    if not target.parent.is_dir():
        print(
            f"error: output directory does not exist: {terminal_text(target.parent)}",
            file=sys.stderr,
        )
        return 1
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(new_text)
            output.flush()
            os.fsync(output.fileno())
        source_mode = (target if target.exists() else args.path).stat().st_mode & 0o777
        os.chmod(temp_path, source_mode)
        os.replace(temp_path, target)
    finally:
        temp_path.unlink(missing_ok=True)
    print(f"\nWrote {terminal_text(target)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
