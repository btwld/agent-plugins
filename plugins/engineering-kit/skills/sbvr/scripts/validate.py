#!/usr/bin/env python3
"""
Validator for the SBVR skill's optional Markdown/YAML house profile.

Runs the checklist from references/checklist.md against a spec file and
prints a report. Supports Markdown and YAML artifacts that follow the
profile schema in references/output-formats.md. It does not establish
general SBVR compliance or business correctness.

Usage:
    python3 /path/to/validate.py path/to/spec.md
    python3 /path/to/validate.py path/to/spec.yaml --format yaml
    python3 /path/to/validate.py path/to/spec.md --json
    python3 /path/to/validate.py path/to/spec.md --strict

Exit codes:
    0  all checks pass (or only INFO-level findings)
    1  one or more WARN findings
    2  one or more FAIL findings

Design notes:
    Each check returns a Finding with a level, a short title, and any
    specific evidence lines. The report groups findings by category so you
    can see structure problems separately from vocabulary problems etc.
    The validator is conservative: it only flags things it can detect with
    high confidence. Things that need human judgment (e.g. "is this rule
    testable?") are not checked.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

LEVEL_FAIL = "FAIL"
LEVEL_WARN = "WARN"
LEVEL_INFO = "INFO"
LEVEL_PASS = "PASS"

LEVEL_RANK = {LEVEL_PASS: 0, LEVEL_INFO: 1, LEVEL_WARN: 2, LEVEL_FAIL: 3}


@dataclass
class Finding:
    category: str
    check: str
    level: str
    message: str
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "check": self.check,
            "level": self.level,
            "message": self.message,
            "evidence": self.evidence,
        }


@dataclass
class ValidationReport:
    spec_path: str
    spec_format: str
    findings: list[Finding] = field(default_factory=list)

    def add(self, f: Finding) -> None:
        self.findings.append(f)

    def counts(self) -> dict[str, int]:
        out = {LEVEL_PASS: 0, LEVEL_INFO: 0, LEVEL_WARN: 0, LEVEL_FAIL: 0}
        for f in self.findings:
            out[f.level] += 1
        return out

    def worst_level(self) -> str:
        return max((f.level for f in self.findings), key=lambda L: LEVEL_RANK[L], default=LEVEL_PASS)

    def exit_code(self) -> int:
        worst = self.worst_level()
        if worst == LEVEL_FAIL:
            return 2
        if worst == LEVEL_WARN:
            return 1
        return 0


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

RULE_BLOCK = re.compile(
    r"^[ \t]*(?:[-*+][ \t]+)?\*\*([A-Z]{1,3}\d+)[:.]?\*\*[ \t]*(.*?)"
    r"(?=^[ \t]*(?:[-*+][ \t]+)?\*\*[A-Z]{1,3}\d+[:.]?\*\*|^#{1,6}[ \t]+|\Z)",
    re.DOTALL | re.MULTILINE,
)
RULE_ID_REF = re.compile(r"\b[A-Z]{1,3}\d+\b")
INLINE_CODE_SPAN = re.compile(r"(`+).*?\1")
URI_TOKEN_RE = re.compile(r"(?:https?://|mailto:)[^\s<>]+", re.IGNORECASE)
REFERENCE_DEFINITION_RE = re.compile(
    r"^[ \t]{0,3}\[[^\]\n]+\]:[ \t]*(?P<destination><[^>\n]*>|\S+)"
)
TERMINAL_CONTROL_RE = re.compile(
    r"[\x00-\x1f\x7f-\x9f\u061c\u200e-\u200f\u202a-\u202e\u2066-\u2069]"
)

# Official SBVR captions that can appear under a vocabulary term.
OFFICIAL_CAPTIONS = {
    "Definition",
    "General Concept",
    "Reference Scheme",
    "Note",
    "Example",
    "Source",
    "Synonym",
    "Description",
    "Necessity",
    "Possibility",
    "See",
    "Dictionary Basis",
    "Concept Type",
    # Fact-type conventions used by the SBVR skill:
    "Preferred",
    "Alternative",
    "Objectified From",
    "Related Fact Types",
    "Related Rules",
    "Constraints",
    "Definitional Rules",
    "Behavioral Rules",
    "Derivation Rules",
}

TECHNICAL_JARGON = [
    r"\bUUID\b",
    r"\bvarchar\b",
    r"\bforeign key\b",
    r"\bprimary key\b",
    r"\bdatabase\b",
    r"\binstantiated\b",
    r"\bserialized\b",
    r"\bdeserialized\b",
    r"\bJSON\b",
    r"\bVARCHAR\b",
    r"\bnullable\b",
    r"\bendpoint\b",
    r"\bHTTP\b",
    r"\bhash\b",
    r"\bdeserialize\b",
]
TECHNICAL_JARGON_RE = re.compile("|".join(TECHNICAL_JARGON))

IMPRECISE_TEMPORAL = [
    r"\bsoon\b",
    r"\btimely\b",
    r"\bwhen possible\b",
    r"\bas soon as possible\b",
    r"\beventually\b",
    r"\bquickly\b",
    r"\bin a timely manner\b",
]
IMPRECISE_TEMPORAL_RE = re.compile("|".join(IMPRECISE_TEMPORAL), re.IGNORECASE)

# Configurable threshold patterns. See grader_iteration_2.py for origin.
# Descriptive numerals (e.g. "18 years of age") are intentionally NOT here.
THRESHOLD_PATTERNS = [
    r"(?:at\s+most|no\s+more\s+than|maximum\s+(?:of)?|up\s+to|fewer\s+than|less\s+than)\s+\d+",
    r"(?:at\s+least|no\s+fewer\s+than|minimum\s+(?:of)?|more\s+than|greater\s+than)\s+\d+",
    r"(?:exactly|precisely)\s+\d+\s+(?:loans?|days?|copies|hours?|members?|reservations?|items?|units?|entries|records?)",
    r"plus\s+\d+\s+(?:day|hour|week|month|minute|second)",
    r"\d+\s*%",
    r"\$\s*\d+",
    r"\d+\s+days?\s+(?:before|after|prior|notice)",
    r"for\s+\d+\s+days?",
    r"within\s+\d+\s+(?:day|hour|minute|second|week|month)",
]
THRESHOLD_RE = re.compile("|".join(f"(?:{p})" for p in THRESHOLD_PATTERNS), re.IGNORECASE)

def markdown_prose(text: str) -> str:
    """Remove fenced and inline code while preserving Markdown prose lines."""
    output: list[str] = []
    fence_character = ""
    fence_length = 0
    for line in text.splitlines(keepends=True):
        match = re.match(r"\s*(`{3,}|~{3,})", line)
        if match and not fence_character:
            marker = match.group(1)
            fence_character = marker[0]
            fence_length = len(marker)
            continue
        if match and fence_character and match.group(1)[0] == fence_character \
                and len(match.group(1)) >= fence_length:
            fence_character = ""
            fence_length = 0
            continue
        if not fence_character:
            prose_line = INLINE_CODE_SPAN.sub("", line)
            protected = [match.span() for match in URI_TOKEN_RE.finditer(prose_line)]
            reference_definition = REFERENCE_DEFINITION_RE.match(prose_line)
            if reference_definition:
                protected.append(reference_definition.span("destination"))
            for link in re.finditer(r"\]\(", prose_line):
                start = link.end() - 1
                depth = 0
                escaped = False
                for position in range(start, len(prose_line)):
                    character = prose_line[position]
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
            chunks: list[str] = []
            cursor = 0
            for start, end in merged:
                chunks.append(prose_line[cursor:start])
                cursor = end
            chunks.append(prose_line[cursor:])
            output.append("".join(chunks))
    return "".join(output)


def extract_rules(text: str) -> list[tuple[str, str]]:
    return [(m.group(1), m.group(2)) for m in RULE_BLOCK.finditer(text)]


def split_rules_by_kind(rules: list[tuple[str, str]]) -> dict[str, list[tuple[str, str]]]:
    buckets: dict[str, list[tuple[str, str]]] = {}
    for rid, body in rules:
        prefix_match = re.match(r"([A-Z]+)", rid)
        if prefix_match:
            buckets.setdefault(prefix_match.group(1), []).append((rid, body))
    return buckets


def _definition_text(body: str) -> str:
    """Return a term's definition text, supporting both layouts:

      - the ``Definition:`` caption (bold-header style), and
      - the heading + prose style, where the definition is the first
        non-bullet, non-caption line directly under the term heading.

    Returns an empty string when no definition can be found.
    """
    m = re.search(r"Definition:\s*([^\n]+)", body, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(("-", "*")):
            continue
        # Skip caption-like lines such as "Synonym: ...".
        if re.match(r"^[A-Za-z][A-Za-z ]+:", s):
            continue
        return s
    return ""


def extract_vocab_terms(text: str) -> list[tuple[str, str, int]]:
    """Find vocabulary entries, scoped to the Vocabulary section if one exists.

    Returns a list of (name, entry_body, line_number). Two layouts are supported:

      - Bold header (``**name**`` on its own line) followed by at least one
        SBVR caption (Definition, Reference Scheme, etc.).
      - Heading entry (``#### name``, deeper than the ``###`` domain groups)
        whose definition is the prose directly under the heading; secondary
        captions (Synonym, Note, ...) appear as bullets.

    Entries whose name starts with 'Fact Type:' or that look like rule ids are
    excluded because those do not belong to the vocabulary.
    """
    vocab_section = find_section(text, r"vocabulary")
    if vocab_section:
        section_text, section_line = vocab_section
        line_offset = section_line
    else:
        section_text = text
        line_offset = 0

    results: list[tuple[str, str, int]] = []
    lines = section_text.splitlines()
    # Legacy bold-header term (**name**). Still accepted for backward
    # compatibility with older specs; the canonical format is the #### heading.
    bold_re = re.compile(r"^\s*\*\*([^*\n]+?)\*\*\s*$")
    # Term headings sit below the domain-group headings (###); the skill
    # standard uses #### for terms, so accept heading level 4+.
    heading_re = re.compile(r"^\s*#{4,6}\s+(.+?)\s*#*\s*$")
    caption_re = re.compile(
        r"^\s*-?\s*(?:" + "|".join(re.escape(c) for c in OFFICIAL_CAPTIONS) + r")\s*:",
        re.IGNORECASE,
    )

    def collect_body(start: int) -> tuple[str, bool]:
        body_lines: list[str] = []
        has_caption = False
        for j in range(start + 1, len(lines)):
            nxt = lines[j]
            if bold_re.match(nxt):
                break
            if re.match(r"^\s*\*\*[A-Z]{1,3}\d+", nxt):
                break
            if re.match(r"^#+\s", nxt):
                break
            body_lines.append(nxt)
            if caption_re.match(nxt):
                has_caption = True
        return "\n".join(body_lines), has_caption

    for i, line in enumerate(lines):
        bold_m = bold_re.match(line)
        head_m = heading_re.match(line) if not bold_m else None
        if bold_m:
            name = bold_m.group(1).strip()
        elif head_m:
            name = head_m.group(1).strip()
        else:
            continue
        # Skip rule headings (e.g. **B1:**) and fact types.
        if re.match(r"^[A-Z]{1,3}\d+\s*:", name):
            continue
        if name.lower().startswith("fact type:"):
            continue
        body, has_caption = collect_body(i)
        # Bold entries require an SBVR caption (unchanged behavior). Heading
        # entries qualify on a caption OR a non-empty body (the prose definition).
        if has_caption or (head_m is not None and body.strip()):
            results.append((name, body, i + 1 + line_offset))
    return results


def find_section(text: str, heading_pattern: str) -> tuple[str, int] | None:
    """Return (section_body, start_line) for the first heading matching the
    pattern, stopping at the next heading of EQUAL or HIGHER level (so
    sub-headings inside the section stay part of the body)."""
    pattern = re.compile(
        r"(?im)^(#+)\s*(?:part\s*\d+\s*[:.]?\s*)?" + heading_pattern + r"\b.*$",
        re.MULTILINE,
    )
    m = pattern.search(text)
    if not m:
        return None
    level = len(m.group(1))
    start = m.end()
    # Next heading at same or higher level (i.e., same or fewer '#' characters).
    same_or_higher = re.compile(r"(?m)^(#{1," + str(level) + r"})\s")
    next_head = same_or_higher.search(text, pos=start)
    end = next_head.start() if next_head else len(text)
    start_line = text[: m.start()].count("\n") + 1
    return (text[start:end], start_line)


def find_rules_section(text: str) -> tuple[str, int] | None:
    """Return the combined rules section body.

    Handles two layouts:
      - Single "## Part N: Rules" heading with subsections.
      - Multiple "## Part N: Definitional Rules / Derivation Rules / Behavioral Rules"
        headings split across the document. In that case, concatenate them.
    """
    single = find_section(text, r"rules?")
    if single:
        return single

    patterns = [
        r"definitional\s+rules?",
        r"derivation\s+rules?",
        r"behavioral\s+rules?",
        r"operative\s+rules?",
        r"structural\s+rules?",
        r"temporal\s+rules?",
    ]
    combined: list[str] = []
    first_line: int | None = None
    for p in patterns:
        section = find_section(text, p)
        if section:
            combined.append(section[0])
            if first_line is None:
                first_line = section[1]
    if combined:
        return ("\n".join(combined), first_line or 1)
    return None


# ---------------------------------------------------------------------------
# Markdown validation
# ---------------------------------------------------------------------------

def validate_structure(text: str, report: ValidationReport) -> None:
    vocab = find_section(text, r"vocabulary")
    facts = find_section(text, r"fact\s*types?")
    rules = find_rules_section(text)

    def add_struct_finding(name: str, present: bool) -> None:
        if present:
            report.add(Finding("Structure", f"{name} section present", LEVEL_PASS, f"{name} section found"))
        else:
            report.add(Finding("Structure", f"{name} section present", LEVEL_FAIL, f"no {name} section found"))

    add_struct_finding("Vocabulary", bool(vocab))
    add_struct_finding("Fact Types", bool(facts))
    add_struct_finding("Rules", bool(rules))

    # Manual term-index appendix (anti-pattern).
    term_index_re = re.compile(
        r"(?im)^#+\s*(?:appendix[:.]?\s*)?(term\s*index|index\s+of\s+terms|alphabetical\s+(?:term\s+)?index)\b"
    )
    if term_index_re.search(text):
        report.add(
            Finding(
                "Structure",
                "No manual term-index appendix",
                LEVEL_WARN,
                "found a manual term-index / appendix section; the vocabulary IS the index",
                evidence=[m.group(0) for m in term_index_re.finditer(text)],
            )
        )
    else:
        report.add(Finding("Structure", "No manual term-index appendix", LEVEL_PASS, "no duplicate term index"))


def validate_vocabulary(text: str, report: ValidationReport) -> None:
    terms = extract_vocab_terms(text)

    if not terms:
        report.add(
            Finding(
                "Vocabulary",
                "Vocabulary has terms",
                LEVEL_FAIL,
                "no vocabulary entries detected (looked for #### term headings, or bold-name headers followed by official captions)",
            )
        )
        return
    report.add(
        Finding(
            "Vocabulary",
            "Vocabulary has terms",
            LEVEL_PASS,
            f"{len(terms)} vocabulary entries detected",
        )
    )

    # 1. Every term has a definition (either a Definition caption or prose
    #    directly under a heading entry).
    missing_def = [name for name, body, _ in terms if not _definition_text(body)]
    if missing_def:
        report.add(
            Finding(
                "Vocabulary",
                "Every term has a Definition",
                LEVEL_WARN,
                f"{len(missing_def)} terms missing a definition",
                evidence=missing_def[:10],
            )
        )
    else:
        report.add(Finding("Vocabulary", "Every term has a Definition", LEVEL_PASS, "all terms define a definition"))

    # 2. Unofficial captions.
    unofficial: list[str] = []
    caption_line_re = re.compile(r"^\s*-?\s*([A-Z][A-Za-z ]+?)\s*:", re.MULTILINE)
    for name, body, _ in terms:
        for m in caption_line_re.finditer(body):
            caption = m.group(1).strip()
            # Only flag captions that look like captions, not sentence fragments.
            if len(caption.split()) > 3:
                continue
            if caption not in OFFICIAL_CAPTIONS and caption.title() not in OFFICIAL_CAPTIONS:
                unofficial.append(f"{name}: '{caption}'")
    if unofficial:
        report.add(
            Finding(
                "Vocabulary",
                "Only official SBVR captions",
                LEVEL_WARN,
                f"{len(unofficial)} unofficial caption(s) found; allowed set: {sorted(OFFICIAL_CAPTIONS)}",
                evidence=unofficial[:10],
            )
        )
    else:
        report.add(Finding("Vocabulary", "Only official SBVR captions", LEVEL_PASS, "all captions are official"))

    # 3. Technical jargon in definitions.
    jargon_hits: list[str] = []
    for name, body, _ in terms:
        matches = TECHNICAL_JARGON_RE.findall(_definition_text(body))
        if matches:
            jargon_hits.append(f"{name}: {matches}")
    if jargon_hits:
        report.add(
            Finding(
                "Vocabulary",
                "No technical jargon in definitions",
                LEVEL_FAIL,
                f"{len(jargon_hits)} term(s) contain technical jargon (UUID, varchar, foreign key, database, etc.)",
                evidence=jargon_hits[:10],
            )
        )
    else:
        report.add(
            Finding("Vocabulary", "No technical jargon in definitions", LEVEL_PASS, "no jargon detected")
        )

    # 4. Circular definitions (term body references its own name).
    circular: list[str] = []
    for name, body, _ in terms:
        definition = _definition_text(body)
        if not definition:
            continue
        definition_lower = definition.lower()
        name_lower = name.lower().strip()
        # A term is circular if its definition uses the same (multi-word or
        # single-word) noun as the term name itself. Single-letter names are
        # excluded to avoid false positives.
        if len(name_lower) >= 4 and re.search(
            r"\b" + re.escape(name_lower) + r"\b", definition_lower
        ):
            circular.append(f"{name}: '{definition.strip()[:80]}'")
    if circular:
        report.add(
            Finding(
                "Vocabulary",
                "No circular definitions",
                LEVEL_FAIL,
                f"{len(circular)} term(s) appear to define themselves",
                evidence=circular[:10],
            )
        )
    else:
        report.add(
            Finding("Vocabulary", "No circular definitions", LEVEL_PASS, "no circular definitions detected")
        )


# Legacy bold fact-type header (**Fact Type: ...** or **lowercase phrase**).
# Still accepted for backward compatibility; the canonical format is a #### heading.
FACT_TYPE_HEADER_RE = re.compile(
    r"^\s*\*\*(?:Fact Type:\s*)?([a-z][^*\n]+?)\*\*\s*$",
    re.MULTILINE,
)


def extract_fact_types(text: str) -> list[str]:
    """Return a list of fact type phrases from the Fact Types section.

    Supports two layouts:
      - Bullet lines like `- member borrows copy`
      - Bold entries like `**Fact Type: member borrows copy**`
    """
    section = find_section(text, r"fact\s*types?")
    if not section:
        return []
    body, _ = section

    results: list[str] = []
    for m in FACT_TYPE_HEADER_RE.finditer(body):
        phrase = m.group(1).strip()
        if phrase and re.search(r"\w+\s+\w+\s+\w+", phrase):
            results.append(phrase)

    # Heading-style entries (#### subject verb object), deeper than the ###
    # domain groups. The heading text is the fact type signature.
    for m in re.finditer(r"^\s*#{4,6}\s+(.+?)\s*#*\s*$", body, re.MULTILINE):
        phrase = m.group(1).strip()
        if phrase.lower().startswith("fact type:"):
            phrase = phrase.split(":", 1)[1].strip()
        if phrase and phrase not in results and re.search(r"\w+\s+\w+\s+\w+", phrase):
            results.append(phrase)

    # Also allow plain bullet-style fact type lines.
    for line in body.splitlines():
        stripped = line.strip().lstrip("-*").strip()
        if stripped.lower().startswith("fact type:"):
            phrase = stripped.split(":", 1)[1].strip()
            if phrase not in results and re.search(r"\w+\s+\w+\s+\w+", phrase):
                results.append(phrase)
    return results


def validate_fact_types(text: str, report: ValidationReport) -> None:
    section = find_section(text, r"fact\s*types?")
    if not section:
        return

    fact_types = extract_fact_types(text)
    if not fact_types:
        report.add(
            Finding(
                "Fact Types",
                "Fact Types section has content",
                LEVEL_WARN,
                "fact types section has no detectable fact type entries (expected #### headings, bold entries, or bullet lines)",
            )
        )
        return
    report.add(
        Finding(
            "Fact Types",
            "Fact Types section has content",
            LEVEL_PASS,
            f"{len(fact_types)} fact type entries detected",
        )
    )

    vague_cardinality = [
        ft for ft in fact_types
        if re.search(r"\bhas\s+(?:many|some|one or more)\b", ft, re.IGNORECASE)
    ]
    if vague_cardinality:
        report.add(
            Finding(
                "Fact Types",
                "Quantification uses SBVR phrasing",
                LEVEL_WARN,
                "fact types use vague cardinality ('has many', 'has some'); prefer 'at least one', 'zero or more', etc.",
                evidence=vague_cardinality[:5],
            )
        )
    else:
        report.add(
            Finding("Fact Types", "Quantification uses SBVR phrasing", LEVEL_PASS, "no vague cardinality found")
        )


def validate_rules(text: str, report: ValidationReport) -> None:
    rules = extract_rules(text)
    if not rules:
        report.add(Finding("Rules", "Rules present", LEVEL_FAIL, "no rules found (looked for **D1:**, **B1:**, etc.)"))
        return
    report.add(Finding("Rules", "Rules present", LEVEL_PASS, f"{len(rules)} rules found"))

    seen_rule_ids: set[str] = set()
    duplicate_rule_ids: set[str] = set()
    for rule_id, _ in rules:
        if rule_id in seen_rule_ids:
            duplicate_rule_ids.add(rule_id)
        seen_rule_ids.add(rule_id)
    if duplicate_rule_ids:
        report.add(
            Finding(
                "Rules",
                "Rule ids are unique",
                LEVEL_FAIL,
                f"{len(duplicate_rule_ids)} duplicate rule id(s) found",
                evidence=sorted(duplicate_rule_ids),
            )
        )
    else:
        report.add(
            Finding("Rules", "Rule ids are unique", LEVEL_PASS, "all rule ids are unique")
        )

    by_kind = split_rules_by_kind(rules)
    def_rules = by_kind.get("D", [])
    beh_rules = by_kind.get("B", [])
    der_rules = by_kind.get("DR", [])

    # 1. Definitional keyword check.
    if def_rules:
        wrong = [
            rid for rid, body in def_rules
            if not re.search(r"^\s*It is (necessary|impossible) that", body)
        ]
        if wrong:
            report.add(
                Finding(
                    "Rules",
                    "Definitional rules use necessary/impossible",
                    LEVEL_FAIL,
                    f"{len(wrong)} definitional rules use the wrong keyword",
                    evidence=wrong[:10],
                )
            )
        else:
            report.add(
                Finding(
                    "Rules",
                    "Definitional rules use necessary/impossible",
                    LEVEL_PASS,
                    f"{len(def_rules)} definitional rules all correct",
                )
            )

    # 2. Behavioral keyword check.
    if beh_rules:
        wrong = [
            rid for rid, body in beh_rules
            if not re.search(r"^\s*It is (obligatory|prohibited|permitted) that", body)
        ]
        if wrong:
            report.add(
                Finding(
                    "Rules",
                    "Behavioral rules use obligatory/prohibited/permitted",
                    LEVEL_FAIL,
                    f"{len(wrong)} behavioral rules use the wrong keyword",
                    evidence=wrong[:10],
                )
            )
        else:
            report.add(
                Finding(
                    "Rules",
                    "Behavioral rules use obligatory/prohibited/permitted",
                    LEVEL_PASS,
                    f"{len(beh_rules)} behavioral rules all correct",
                )
            )

    # 3. Misclassified rules: definitional keyword in a B-rule or vice versa.
    misclassified: list[str] = []
    for rid, body in beh_rules:
        if re.search(r"^\s*It is (necessary|impossible) that", body):
            misclassified.append(f"{rid} is categorized as behavioral but uses a definitional keyword")
    for rid, body in def_rules:
        if re.search(r"^\s*It is (obligatory|prohibited|permitted) that", body):
            misclassified.append(f"{rid} is categorized as definitional but uses a behavioral keyword")
    if misclassified:
        report.add(
            Finding(
                "Rules",
                "Rule category matches keyword",
                LEVEL_FAIL,
                f"{len(misclassified)} rule(s) misclassified",
                evidence=misclassified[:10],
            )
        )
    else:
        report.add(
            Finding("Rules", "Rule category matches keyword", LEVEL_PASS, "no misclassified rules")
        )

    # 4. "The system" actor check (in rule bodies only).
    system_hits = [rid for rid, body in rules if re.search(r"(?i)\bthe system\b", body)]
    if system_hits:
        report.add(
            Finding(
                "Rules",
                "No 'the system' actor",
                LEVEL_FAIL,
                f"{len(system_hits)} rule(s) use 'the system' as actor; rewrite passively",
                evidence=system_hits[:10],
            )
        )
    else:
        report.add(Finding("Rules", "No 'the system' actor", LEVEL_PASS, "no 'the system' in rule bodies"))

    # 5. Threshold leakage: configurable digits inside rule statements.
    leaks: list[str] = []
    for rid, body in rules:
        # Only scan the first sentence (the rule statement itself), not any
        # Note or Example caption that might live inside the same block.
        statement = body.split("\n", 1)[0]
        stripped = RULE_ID_REF.sub(" ", statement)
        matches = THRESHOLD_RE.findall(stripped)
        if matches:
            leaks.append(f"{rid}: {matches}")
    if leaks:
        report.add(
            Finding(
                "Rules",
                "No threshold leakage (policy pattern)",
                LEVEL_FAIL,
                f"{len(leaks)} rule(s) embed configurable thresholds; lift them into a policy noun concept",
                evidence=leaks[:10],
            )
        )
    else:
        report.add(
            Finding(
                "Rules",
                "No threshold leakage (policy pattern)",
                LEVEL_PASS,
                "no configurable thresholds found in rule statements",
            )
        )

    # 6. Double negatives.
    double_neg: list[str] = []
    for rid, body in rules:
        statement = body.split("\n", 1)[0].lower()
        if re.search(r"impossible that[^.]*\bnot\b", statement):
            double_neg.append(rid)
        elif re.search(r"necessary that[^.]*\bnot\b[^.]*\bwithout\b", statement):
            double_neg.append(rid)
    if double_neg:
        report.add(
            Finding(
                "Rules",
                "No double negatives",
                LEVEL_WARN,
                f"{len(double_neg)} rule(s) contain a double-negative construction; rewrite as positive",
                evidence=double_neg[:10],
            )
        )
    else:
        report.add(Finding("Rules", "No double negatives", LEVEL_PASS, "no double negatives"))

    # 7. Imprecise temporal language.
    vague: list[str] = []
    for rid, body in rules:
        statement = body.split("\n", 1)[0]
        if IMPRECISE_TEMPORAL_RE.search(statement):
            vague.append(f"{rid}: {IMPRECISE_TEMPORAL_RE.findall(statement)}")
    if vague:
        report.add(
            Finding(
                "Rules",
                "No imprecise temporal language",
                LEVEL_WARN,
                f"{len(vague)} rule(s) use vague timing words ('soon', 'timely', 'when possible')",
                evidence=vague[:10],
            )
        )
    else:
        report.add(
            Finding("Rules", "No imprecise temporal language", LEVEL_PASS, "no vague temporal words")
        )

    # 8. Procedural style (then/first/afterwards chains inside a single rule).
    procedural: list[str] = []
    for rid, body in rules:
        statement = body.split("\n", 1)[0].lower()
        if re.search(r"\b(?:then|afterwards?|next)\b.*\b(?:then|afterwards?|next)\b", statement):
            procedural.append(rid)
        elif re.search(r"\bfirst[,\s].*,\s*then\b", statement):
            procedural.append(rid)
    if procedural:
        report.add(
            Finding(
                "Rules",
                "No procedural rule style",
                LEVEL_WARN,
                f"{len(procedural)} rule(s) look procedural (step-then-step); rewrite declaratively",
                evidence=procedural[:10],
            )
        )
    else:
        report.add(Finding("Rules", "No procedural rule style", LEVEL_PASS, "no procedural chains in rules"))

    # 9. Rule numbering sequential per prefix.
    numbering_issues: list[str] = []
    for prefix, bucket in by_kind.items():
        nums = [int(re.match(r"[A-Z]+(\d+)", rid).group(1)) for rid, _ in bucket]
        expected = list(range(1, len(nums) + 1))
        if nums != expected:
            numbering_issues.append(f"{prefix}: ids={nums}, expected={expected}")
    if numbering_issues:
        report.add(
            Finding(
                "Rules",
                "Rule numbering is sequential",
                LEVEL_WARN,
                "rule ids have gaps or are out of order",
                evidence=numbering_issues,
            )
        )
    else:
        report.add(
            Finding(
                "Rules",
                "Rule numbering is sequential",
                LEVEL_PASS,
                "rule ids are sequential per category",
            )
        )

    # 10. Derivation rules use formula notation.
    if der_rules:
        bad_formula = [rid for rid, body in der_rules if "=" not in body.split("\n", 1)[0]]
        if bad_formula:
            report.add(
                Finding(
                    "Rules",
                    "Derivation rules use formula notation",
                    LEVEL_WARN,
                    f"{len(bad_formula)} derivation rules missing 'x = ...' formula",
                    evidence=bad_formula[:10],
                )
            )
        else:
            report.add(
                Finding(
                    "Rules",
                    "Derivation rules use formula notation",
                    LEVEL_PASS,
                    f"{len(der_rules)} derivation rules use formulas",
                )
            )


def validate_cross_references(text: str, report: ValidationReport) -> None:
    terms = [name.lower() for name, _, _ in extract_vocab_terms(text)]
    term_set = set(terms)

    facts_section = find_section(text, r"fact\s*types?")
    rules_section = find_rules_section(text)
    search_text_parts = []
    if facts_section:
        search_text_parts.append(facts_section[0])
    if rules_section:
        search_text_parts.append(rules_section[0])

    search_source = markdown_prose("\n".join(search_text_parts))
    if not search_source:
        return
    search_text = search_source.lower()

    if term_set:
        used: set[str] = set()
        for term in term_set:
            if re.search(r"\b" + re.escape(term) + r"\b", search_text):
                used.add(term)

        orphans = sorted(term_set - used)
        if orphans:
            report.add(
                Finding(
                    "Cross-References",
                    "No orphan vocabulary terms",
                    LEVEL_WARN,
                    f"{len(orphans)} term(s) are defined but never used in a fact type or rule",
                    evidence=orphans[:15],
                )
            )
        else:
            report.add(
                Finding(
                    "Cross-References",
                    "No orphan vocabulary terms",
                    LEVEL_PASS,
                    "every vocabulary term is referenced somewhere",
                )
            )

    defined_rule_ids = {rule_id for rule_id, _ in extract_rules(search_source)}
    referenced_rule_ids = set(RULE_ID_REF.findall(search_source))
    unresolved_rule_ids = sorted(referenced_rule_ids - defined_rule_ids)
    if unresolved_rule_ids:
        report.add(
            Finding(
                "Cross-References",
                "All rule references resolve",
                LEVEL_FAIL,
                f"{len(unresolved_rule_ids)} rule reference(s) are undefined",
                evidence=unresolved_rule_ids[:15],
            )
        )
    else:
        report.add(
            Finding(
                "Cross-References",
                "All rule references resolve",
                LEVEL_PASS,
                "every Markdown rule reference resolves",
            )
        )


# ---------------------------------------------------------------------------
# YAML validation (canonical schema)
# ---------------------------------------------------------------------------

def yaml_mapping_list(
    value: object,
    *,
    category: str,
    field_name: str,
    wrapper_name: str,
    report: ValidationReport,
) -> list[dict]:
    """Return canonical mapping entries and report structural failures."""
    if isinstance(value, dict) and isinstance(value.get(wrapper_name), list):
        report.add(
            Finding(
                category,
                f"{field_name} is a flat list",
                LEVEL_WARN,
                f"{field_name} is nested under '{wrapper_name}:'; the canonical schema uses a direct list",
            )
        )
        value = value[wrapper_name]
    elif not isinstance(value, list):
        report.add(
            Finding(
                category,
                f"{field_name} is a flat list",
                LEVEL_FAIL,
                f"{field_name} should be a list, got {type(value).__name__}",
            )
        )
        return []

    if not value:
        report.add(
            Finding(
                category,
                f"{field_name} has entries",
                LEVEL_FAIL,
                f"{field_name} must contain at least one entry",
            )
        )
        return []

    invalid = [str(index) for index, entry in enumerate(value) if not isinstance(entry, dict)]
    if invalid:
        report.add(
            Finding(
                category,
                f"{field_name} entries are mappings",
                LEVEL_FAIL,
                f"{len(invalid)} {field_name} entry or entries are not mappings",
                evidence=invalid[:10],
            )
        )
    return [entry for entry in value if isinstance(entry, dict)]


def validate_yaml_entry_shape(
    entries: list[dict],
    *,
    category: str,
    label: str,
    required: set[str],
    allowed: set[str],
    report: ValidationReport,
) -> None:
    missing: list[str] = []
    extras: list[str] = []
    for index, entry in enumerate(entries):
        entry_id = str(entry.get("id", f"entry {index}"))
        absent = [
            field
            for field in sorted(required)
            if field not in entry
            or entry[field] is None
            or (isinstance(entry[field], str) and not entry[field].strip())
        ]
        if absent:
            missing.append(f"{entry_id}: {', '.join(absent)}")
        unexpected = sorted(str(key) for key in set(entry) - allowed)
        if unexpected:
            extras.append(f"{entry_id}: {', '.join(unexpected)}")

    if missing:
        report.add(
            Finding(
                category,
                f"Every {label} has required fields",
                LEVEL_FAIL,
                f"{len(missing)} {label} entry or entries have missing fields",
                evidence=missing[:10],
            )
        )
    elif entries:
        report.add(
            Finding(
                category,
                f"Every {label} has required fields",
                LEVEL_PASS,
                f"all {len(entries)} {label} entries have required fields",
            )
        )

    if extras:
        report.add(
            Finding(
                category,
                f"No ad-hoc {label} fields",
                LEVEL_FAIL,
                f"{len(extras)} {label} entry or entries use fields outside the canonical schema",
                evidence=extras[:10],
            )
        )


def collect_yaml_ids(
    entries: list[dict],
    *,
    category: str,
    label: str,
    pattern: str,
    report: ValidationReport,
) -> set[str]:
    ids: set[str] = set()
    invalid: list[str] = []
    duplicates: set[str] = set()
    for entry in entries:
        value = entry.get("id")
        entry_id = value if isinstance(value, str) else str(value or "?")
        if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
            invalid.append(entry_id)
            continue
        if value in ids:
            duplicates.add(value)
        ids.add(value)

    if invalid:
        report.add(
            Finding(
                category,
                f"{label} ids use the canonical format",
                LEVEL_FAIL,
                f"{len(invalid)} {label} id or ids use an invalid format",
                evidence=invalid[:10],
            )
        )
    elif entries:
        report.add(
            Finding(
                category,
                f"{label} ids use the canonical format",
                LEVEL_PASS,
                f"{len(ids)} {label} ids use the canonical format",
            )
        )
    if duplicates:
        report.add(
            Finding(
                category,
                f"{label} ids are unique",
                LEVEL_FAIL,
                f"{len(duplicates)} duplicate {label} id or ids found",
                evidence=sorted(duplicates),
            )
        )
    return ids


def validate_yaml_spec(text: str, report: ValidationReport) -> None:
    try:
        import yaml  # type: ignore
    except ImportError:
        report.add(
            Finding(
                "Structure",
                "YAML parse",
                LEVEL_FAIL,
                "PyYAML is required for YAML validation; install it in the selected "
                "Python environment before retrying",
            )
        )
        return

    fence = re.search(r"```ya?ml\s*\n(.*?)```", text, re.DOTALL)
    yaml_text = fence.group(1) if fence else text

    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        report.add(Finding("Structure", "YAML parse", LEVEL_FAIL, f"yaml.safe_load failed: {exc}"))
        return

    if not isinstance(data, dict):
        report.add(Finding("Structure", "YAML parse", LEVEL_FAIL, "top-level YAML must be a mapping"))
        return
    report.add(Finding("Structure", "YAML parse", LEVEL_PASS, "yaml parses"))

    canonical = {"specification", "vocabulary", "fact_types", "rules"}
    top_keys = set(data.keys())
    missing = canonical - top_keys
    if missing:
        report.add(
            Finding(
                "Structure",
                "Canonical top-level keys",
                LEVEL_FAIL,
                f"missing canonical keys: {sorted(missing, key=str)}",
            )
        )
    else:
        report.add(
            Finding("Structure", "Canonical top-level keys", LEVEL_PASS, "all canonical keys present")
        )

    extras = top_keys - canonical
    if extras:
        report.add(
            Finding(
                "Structure",
                "No ad-hoc top-level keys",
                LEVEL_FAIL,
                f"unexpected top-level keys: {sorted(extras, key=str)}",
            )
        )

    spec = data.get("specification")
    declared_vocabularies: set[str] | None = None
    if not isinstance(spec, dict):
        report.add(
            Finding(
                "Structure",
                "specification metadata complete",
                LEVEL_FAIL,
                "specification must be a mapping",
            )
        )
    else:
        missing_meta = [
            key
            for key in ("title", "version", "scope")
            if key not in spec
            or not isinstance(spec[key], str)
            or not spec[key].strip()
        ]
        if missing_meta:
            report.add(
                Finding(
                    "Structure",
                    "specification metadata complete",
                    LEVEL_FAIL,
                    f"specification block missing: {missing_meta}",
                )
            )
        else:
            report.add(
                Finding(
                    "Structure",
                    "specification metadata complete",
                    LEVEL_PASS,
                    "title, version, scope all present",
                )
            )
        unexpected_meta = sorted(
            set(spec) - {"title", "version", "scope", "vocabularies"},
            key=str,
        )
        if unexpected_meta:
            report.add(
                Finding(
                    "Structure",
                    "No ad-hoc specification fields",
                    LEVEL_FAIL,
                    f"unexpected specification fields: {unexpected_meta}",
                )
            )
        if "vocabularies" in spec:
            vocabularies = spec["vocabularies"]
            if not isinstance(vocabularies, list) or not vocabularies \
                    or not all(isinstance(item, str) and item.strip() for item in vocabularies):
                report.add(
                    Finding(
                        "Structure",
                        "Multi-vocabulary metadata is valid",
                        LEVEL_FAIL,
                        "specification.vocabularies must be a non-empty string list",
                    )
                )
            elif len(vocabularies) != len(set(vocabularies)):
                report.add(
                    Finding(
                        "Structure",
                        "Multi-vocabulary metadata is valid",
                        LEVEL_FAIL,
                        "specification.vocabularies contains duplicate names",
                    )
                )
            else:
                declared_vocabularies = set(vocabularies)
                report.add(
                    Finding(
                        "Structure",
                        "Multi-vocabulary metadata is valid",
                        LEVEL_PASS,
                        f"{len(vocabularies)} vocabulary names declared",
                    )
                )

    vocab = yaml_mapping_list(
        data.get("vocabulary"),
        category="Vocabulary",
        field_name="vocabulary",
        wrapper_name="terms",
        report=report,
    )
    fact_types = yaml_mapping_list(
        data.get("fact_types"),
        category="Fact Types",
        field_name="fact_types",
        wrapper_name="items",
        report=report,
    )
    rules = yaml_mapping_list(
        data.get("rules"),
        category="Rules",
        field_name="rules",
        wrapper_name="items",
        report=report,
    )

    validate_yaml_entry_shape(
        vocab,
        category="Vocabulary",
        label="term",
        required={"id", "term", "definition"},
        allowed={
            "id", "term", "definition", "reference_scheme", "note",
            "general_concept", "is_policy", "vocabulary",
        },
        report=report,
    )
    validate_yaml_entry_shape(
        fact_types,
        category="Fact Types",
        label="fact type",
        required={"id", "preferred", "references", "quantification"},
        allowed={
            "id", "preferred", "alternative", "references", "quantification", "vocabulary",
        },
        report=report,
    )
    validate_yaml_entry_shape(
        rules,
        category="Rules",
        label="rule",
        required={"id", "type", "statement", "references"},
        allowed={"id", "type", "modality", "statement", "references", "vocabulary"},
        report=report,
    )

    term_ids = collect_yaml_ids(
        vocab,
        category="Vocabulary",
        label="term",
        pattern=r"term-[a-z0-9]+(?:-[a-z0-9]+)*",
        report=report,
    )
    ft_ids = collect_yaml_ids(
        fact_types,
        category="Fact Types",
        label="fact type",
        pattern=r"ft-[a-z0-9]+(?:-[a-z0-9]+)*",
        report=report,
    )
    rule_ids = collect_yaml_ids(
        rules,
        category="Rules",
        label="rule",
        pattern=r"[A-Z]{1,3}[1-9][0-9]*",
        report=report,
    )

    value_shape_problems: list[str] = []
    for index, entry in enumerate(vocab):
        entry_id = str(entry.get("id", f"term {index}"))
        for field_name in ("term", "definition"):
            value = entry.get(field_name)
            if not isinstance(value, str) or not value.strip():
                value_shape_problems.append(f"{entry_id}: {field_name} must be text")
        if "general_concept" in entry and entry["general_concept"] is not None \
                and not isinstance(entry["general_concept"], str):
            value_shape_problems.append(f"{entry_id}: general_concept must be a term id")
        if "is_policy" in entry and not isinstance(entry["is_policy"], bool):
            value_shape_problems.append(f"{entry_id}: is_policy must be boolean")
        for field_name in ("reference_scheme", "note"):
            if field_name in entry and (
                not isinstance(entry[field_name], str) or not entry[field_name].strip()
            ):
                value_shape_problems.append(f"{entry_id}: {field_name} must be text")
    for index, entry in enumerate(fact_types):
        entry_id = str(entry.get("id", f"fact type {index}"))
        preferred = entry.get("preferred")
        if not isinstance(preferred, str) or not preferred.strip():
            value_shape_problems.append(f"{entry_id}: preferred must be text")
        quantification = entry.get("quantification")
        if not isinstance(quantification, list) or not quantification:
            value_shape_problems.append(f"{entry_id}: quantification must be a non-empty list")
        else:
            for quantification_index, item in enumerate(quantification):
                item_label = f"{entry_id}: quantification[{quantification_index}]"
                if not isinstance(item, dict):
                    value_shape_problems.append(f"{item_label} must be a mapping")
                    continue
                unexpected = sorted(
                    str(key) for key in set(item) - {"direction", "statement"}
                )
                missing = sorted({"direction", "statement"} - set(item))
                if unexpected:
                    value_shape_problems.append(
                        f"{item_label} has unexpected fields: {', '.join(unexpected)}"
                    )
                if missing:
                    value_shape_problems.append(
                        f"{item_label} is missing fields: {', '.join(missing)}"
                    )
                for field_name in ("direction", "statement"):
                    value = item.get(field_name)
                    if field_name in item and (
                        not isinstance(value, str) or not value.strip()
                    ):
                        value_shape_problems.append(
                            f"{item_label}.{field_name} must be text"
                        )
        if "alternative" in entry and (
            not isinstance(entry["alternative"], str) or not entry["alternative"].strip()
        ):
            value_shape_problems.append(f"{entry_id}: alternative must be text")
    for index, entry in enumerate(rules):
        entry_id = str(entry.get("id", f"rule {index}"))
        statement = entry.get("statement")
        if not isinstance(statement, str) or not statement.strip():
            value_shape_problems.append(f"{entry_id}: statement must be text")

    all_entries = [*vocab, *fact_types, *rules]
    for index, entry in enumerate(all_entries):
        entry_id = str(entry.get("id", f"entry {index}"))
        if "vocabulary" in entry and (
            not isinstance(entry["vocabulary"], str) or not entry["vocabulary"].strip()
        ):
            value_shape_problems.append(f"{entry_id}: vocabulary must be text")

    if declared_vocabularies is not None:
        for index, entry in enumerate(all_entries):
            entry_id = str(entry.get("id", f"entry {index}"))
            vocabulary = entry.get("vocabulary")
            if not isinstance(vocabulary, str) or vocabulary not in declared_vocabularies:
                value_shape_problems.append(
                    f"{entry_id}: vocabulary must name a declared specification vocabulary"
                )
    else:
        for index, entry in enumerate(all_entries):
            if "vocabulary" in entry:
                entry_id = str(entry.get("id", f"entry {index}"))
                value_shape_problems.append(
                    f"{entry_id}: specification.vocabularies must declare its vocabulary"
                )
    if value_shape_problems:
        report.add(
            Finding(
                "Structure",
                "YAML field values use the canonical types",
                LEVEL_FAIL,
                f"{len(value_shape_problems)} field value or values have invalid types",
                evidence=value_shape_problems[:10],
            )
        )

    id_groups = (("term", term_ids), ("fact type", ft_ids), ("rule", rule_ids))
    cross_type_duplicates: list[str] = []
    for index, (left_label, left_ids) in enumerate(id_groups):
        for right_label, right_ids in id_groups[index + 1:]:
            cross_type_duplicates.extend(
                f"{value}: {left_label} and {right_label}"
                for value in sorted(left_ids & right_ids)
            )
    if cross_type_duplicates:
        report.add(
            Finding(
                "Cross-References",
                "Ids are unique across the file",
                LEVEL_FAIL,
                f"{len(cross_type_duplicates)} id or ids are reused across entry types",
                evidence=cross_type_duplicates[:10],
            )
        )

    circular: list[str] = []
    for entry in vocab:
        term = str(entry.get("term", "")).lower().strip()
        definition = str(entry.get("definition", "")).lower()
        if len(term) >= 4 and re.search(r"\b" + re.escape(term) + r"\b", definition):
            circular.append(str(entry.get("id", "?")))
    if circular:
        report.add(
            Finding(
                "Vocabulary",
                "No circular definitions",
                LEVEL_FAIL,
                f"{len(circular)} term or terms reference themselves in their definition",
                evidence=circular[:10],
            )
        )

    type_problems: list[str] = []
    modality_problems: list[str] = []
    statement_leaks: list[str] = []
    orphan_refs: list[str] = []
    if rules:
        valid_types = {"definitional", "behavioral", "derivation"}
        valid_modality = {"obligation", "prohibition", "permission"}
        for entry in rules:
            rule_id = str(entry.get("id", "?"))
            rule_type = entry.get("type")
            if rule_type not in valid_types:
                type_problems.append(f"{rule_id}: type={rule_type}")
            if rule_type == "behavioral" and entry.get("modality") not in valid_modality:
                modality_problems.append(f"{rule_id}: modality={entry.get('modality')}")
            if rule_type != "behavioral" and "modality" in entry:
                modality_problems.append(f"{rule_id}: modality is only valid for behavioral rules")
            statement = str(entry.get("statement", ""))
            stripped = RULE_ID_REF.sub(" ", statement)
            if THRESHOLD_RE.findall(stripped):
                statement_leaks.append(f"{rule_id}: {THRESHOLD_RE.findall(stripped)}")

        if type_problems:
            report.add(
                Finding(
                    "Rules",
                    "Every rule has a valid type",
                    LEVEL_FAIL,
                    f"{len(type_problems)} rule(s) missing or invalid type",
                    evidence=type_problems[:10],
                )
            )
        else:
            report.add(
                Finding("Rules", "Every rule has a valid type", LEVEL_PASS, f"{len(rules)} rules")
            )
        if modality_problems:
            report.add(
                Finding(
                    "Rules",
                    "Behavioral rules have valid modality",
                    LEVEL_FAIL,
                    f"{len(modality_problems)} behavioral rule(s) missing modality",
                    evidence=modality_problems[:10],
                )
            )
        if statement_leaks:
            report.add(
                Finding(
                    "Rules",
                    "No threshold leakage in statements",
                    LEVEL_FAIL,
                    f"{len(statement_leaks)} rule statement(s) embed thresholds",
                    evidence=statement_leaks[:10],
                )
            )
        else:
            report.add(
                Finding("Rules", "No threshold leakage in statements", LEVEL_PASS, "no threshold leaks")
            )

    valid_reference_ids = term_ids | ft_ids
    for category, entries in (("fact type", fact_types), ("rule", rules)):
        for index, entry in enumerate(entries):
            owner = str(entry.get("id", f"{category} {index}"))
            refs = entry.get("references")
            if not isinstance(refs, list) or not refs:
                orphan_refs.append(f"{owner}: references must be a non-empty list")
                continue
            string_refs = [ref for ref in refs if isinstance(ref, str)]
            if len(string_refs) != len(set(string_refs)):
                orphan_refs.append(f"{owner}: references contains duplicate ids")
            for ref in refs:
                if not isinstance(ref, str) or ref not in valid_reference_ids:
                    orphan_refs.append(f"{owner} -> {ref}")
    for entry in vocab:
        general_concept = entry.get("general_concept")
        if general_concept is not None and (
            not isinstance(general_concept, str) or general_concept not in term_ids
        ):
            orphan_refs.append(f"{entry.get('id', '?')} -> {general_concept}")

    if orphan_refs:
        report.add(
            Finding(
                "Cross-References",
                "All references resolve",
                LEVEL_FAIL,
                f"{len(orphan_refs)} reference(s) point to undefined ids",
                evidence=orphan_refs[:10],
            )
        )
    else:
        report.add(
            Finding("Cross-References", "All references resolve", LEVEL_PASS, "every reference id resolves")
        )


# ---------------------------------------------------------------------------
# Top-level drivers
# ---------------------------------------------------------------------------

def detect_format(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix == ".md":
        return "markdown"
    return None


def validate_file(path: Path, fmt: str) -> ValidationReport:
    report = ValidationReport(spec_path=str(path), spec_format=fmt)
    text = path.read_text()
    if fmt == "yaml":
        validate_yaml_spec(text, report)
    else:
        prose = markdown_prose(text)
        validate_structure(prose, report)
        validate_vocabulary(prose, report)
        validate_fact_types(prose, report)
        validate_rules(prose, report)
        validate_cross_references(prose, report)
    return report


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

COLOR = {
    LEVEL_PASS: "\033[32m",
    LEVEL_INFO: "\033[34m",
    LEVEL_WARN: "\033[33m",
    LEVEL_FAIL: "\033[31m",
}
RESET = "\033[0m"


def terminal_text(value: object) -> str:
    """Replace terminal control characters in human-readable output."""
    return TERMINAL_CONTROL_RE.sub("?", str(value))


def print_report(report: ValidationReport, use_color: bool, show_passing: bool) -> None:
    print(f"SBVR validator report for: {terminal_text(report.spec_path)}")
    print(f"Format: {terminal_text(report.spec_format)}")
    print()

    by_category: dict[str, list[Finding]] = {}
    for f in report.findings:
        by_category.setdefault(f.category, []).append(f)

    for category, findings in by_category.items():
        print(f"## {terminal_text(category)}")
        for f in findings:
            if f.level == LEVEL_PASS and not show_passing:
                continue
            tag = f"[{f.level}]"
            if use_color:
                tag = f"{COLOR.get(f.level, '')}{tag}{RESET}"
            print(f"  {tag} {terminal_text(f.check)}: {terminal_text(f.message)}")
            for line in f.evidence[:5]:
                print(f"      - {terminal_text(line)}")
        print()

    counts = report.counts()
    total = sum(counts.values())
    print(
        f"Summary: {counts[LEVEL_PASS]} pass, {counts[LEVEL_INFO]} info, "
        f"{counts[LEVEL_WARN]} warn, {counts[LEVEL_FAIL]} fail "
        f"({total} checks)"
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate an SBVR spec file against skill best practices.")
    parser.add_argument("path", type=Path, help="Path to the spec file (.md, .yaml, .yml)")
    parser.add_argument(
        "--format",
        choices=["auto", "markdown", "yaml"],
        default="auto",
        help="Spec format (default: auto-detect by extension)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report instead of console text")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors in text output")
    parser.add_argument("--show-passing", action="store_true", help="Show PASS findings (default: only non-pass)")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat WARN as FAIL for exit code purposes",
    )
    args = parser.parse_args(argv)

    if args.path.is_symlink():
        print(f"error: refusing symlinked input: {terminal_text(args.path)}", file=sys.stderr)
        return 2
    if not args.path.is_file():
        print(f"error: {terminal_text(args.path)} is not a file", file=sys.stderr)
        return 2

    fmt = args.format if args.format != "auto" else detect_format(args.path)
    if fmt is None:
        print(
            "error: cannot detect the format from this file suffix: "
            f"{terminal_text(args.path)}",
            file=sys.stderr,
        )
        return 2
    try:
        report = validate_file(args.path, fmt)
    except (OSError, UnicodeError) as exc:
        print(
            f"error: cannot read {terminal_text(args.path)}: {terminal_text(exc)}",
            file=sys.stderr,
        )
        return 2

    if args.json:
        print(json.dumps({
            "spec_path": report.spec_path,
            "spec_format": report.spec_format,
            "findings": [f.to_dict() for f in report.findings],
            "counts": report.counts(),
            "worst_level": report.worst_level(),
        }, indent=2))
    else:
        use_color = not args.no_color and sys.stdout.isatty()
        print_report(report, use_color=use_color, show_passing=args.show_passing)

    exit_code = report.exit_code()
    if args.strict and report.counts()[LEVEL_WARN] > 0 and exit_code < 2:
        exit_code = 2
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
