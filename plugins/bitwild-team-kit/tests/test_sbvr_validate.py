#!/usr/bin/env python3
"""Regression tests for the SBVR validator helper."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "sbvr"
    / "scripts"
    / "validate.py"
)
SPEC = importlib.util.spec_from_file_location("sbvr_validate", SCRIPT)
assert SPEC and SPEC.loader
sbvr_validate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = sbvr_validate
SPEC.loader.exec_module(sbvr_validate)


class SbvrValidateTests(unittest.TestCase):
    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = sbvr_validate.main(argv)
        return status, stdout.getvalue(), stderr.getvalue()

    def run_yaml_payload(self, payload: object) -> tuple[int, str, str]:
        fake_yaml = SimpleNamespace(
            YAMLError=Exception,
            safe_load=lambda _: payload,
        )
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "spec.yaml"
            source.write_text("fixture: true\n", encoding="utf-8")
            with mock.patch.dict(sys.modules, {"yaml": fake_yaml}):
                return self.run_main([str(source), "--json"])

    def test_rejects_directory_and_unknown_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            unknown = root / "rules.txt"
            unknown.write_text("rules\n", encoding="utf-8")

            directory_status, _, directory_error = self.run_main([str(root)])
            suffix_status, _, suffix_error = self.run_main([str(unknown)])

        self.assertEqual(directory_status, 2)
        self.assertIn("is not a file", directory_error)
        self.assertEqual(suffix_status, 2)
        self.assertIn("cannot detect the format", suffix_error)

    def test_json_report_identifies_an_undefined_reference(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "spec.md"
            source.write_text(
                "# Example\n\n"
                "## Vocabulary\n\n"
                "#### order\n\nAn order is a request.\n\n"
                "## Fact Types\n\norder is submitted\n\n"
                "## Rules\n\n**B1:** It is obligatory that an order references D9.\n",
                encoding="utf-8",
            )
            status, stdout, stderr = self.run_main([str(source), "--json"])

        self.assertIn(status, {1, 2})
        self.assertFalse(stderr)
        self.assertIn('"All rule references resolve"', stdout)
        self.assertIn("D9", stdout)

    def test_rule_references_inside_code_are_not_validation_edges(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "spec.md"
            source.write_text(
                "# Example\n\n"
                "## Vocabulary\n\n"
                "#### order\n\nAn order is a request.\n\n"
                "## Fact Types\n\norder is submitted\n\n"
                "## Rules\n\n"
                "**B1:** It is obligatory that an order is submitted.\n\n"
                "The token `D9` is an implementation example.\n\n"
                "```text\nST77 is sample output.\n```\n",
                encoding="utf-8",
            )
            _, stdout, stderr = self.run_main([str(source), "--json"])

        self.assertFalse(stderr)
        self.assertIn('"All rule references resolve"', stdout)
        self.assertNotIn("D9", stdout)
        self.assertNotIn("ST77", stdout)

    def test_rule_ids_inside_link_destinations_are_not_validation_edges(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "spec.md"
            source.write_text(
                "# Example\n\n"
                "## Vocabulary\n\n"
                "#### order\n\nA customer request.\n\n"
                "## Fact Types\n\norder is submitted\n\n"
                "## Rules\n\n"
                "**B1:** It is obligatory that an order is submitted.\n\n"
                "See [the source](https://example.test/rules/D9).\n",
                encoding="utf-8",
            )
            _, stdout, stderr = self.run_main([str(source), "--json"])

        self.assertFalse(stderr)
        self.assertIn('"All rule references resolve"', stdout)
        self.assertNotIn("D9", stdout)

    def test_link_stripping_preserves_following_prose(self) -> None:
        prose = sbvr_validate.markdown_prose(
            "See [the source](https://example.test/rules/D9). Then apply B2.\n"
        )

        self.assertNotIn("D9", prose)
        self.assertIn("Then apply B2.", prose)

    def test_rule_blocks_inside_code_are_not_rules(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "spec.md"
            source.write_text(
                "# Example\n\n"
                "## Vocabulary\n\n"
                "#### order\n\nAn order is a request.\n\n"
                "## Fact Types\n\norder is submitted\n\n"
                "## Rules\n\n"
                "**B1:** It is obligatory that an order is submitted.\n\n"
                "```markdown\n"
                "**B9:** It is obligatory that sample code is ignored.\n"
                "```\n",
                encoding="utf-8",
            )
            _, stdout, stderr = self.run_main([str(source), "--json"])

        self.assertFalse(stderr)
        self.assertIn('"message": "1 rules found"', stdout)
        self.assertNotIn("B9", stdout)

    def test_duplicate_markdown_rule_ids_fail(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "spec.md"
            source.write_text(
                "# Example\n\n"
                "## Vocabulary\n\n"
                "#### order\n\nAn order is a request.\n\n"
                "## Fact Types\n\norder is submitted\n\n"
                "## Rules\n\n"
                "**B1:** It is obligatory that an order is submitted.\n\n"
                "**B1:** It is obligatory that an order is reviewed.\n",
                encoding="utf-8",
            )
            status, stdout, stderr = self.run_main([str(source), "--json"])

        self.assertEqual(status, 2)
        self.assertFalse(stderr)
        self.assertIn('"check": "Rule ids are unique"', stdout)
        self.assertIn("B1", stdout)

    def test_inline_bold_rule_example_is_not_a_rule(self) -> None:
        rules = sbvr_validate.extract_rules(
            "See **B9:** as an inline example.\n\n"
            "**B4:** It is obligatory that an order is reviewed.\n"
        )

        self.assertEqual([rule_id for rule_id, _ in rules], ["B4"])

    def test_jargon_in_a_note_does_not_fail_the_definition_check(self) -> None:
        report = sbvr_validate.ValidationReport("fixture.md", "markdown")
        sbvr_validate.validate_vocabulary(
            "## Vocabulary\n\n"
            "#### order\n\n"
            "A customer request.\n\n"
            "- Note: The implementation stores a database identifier.\n",
            report,
        )

        finding = next(
            item
            for item in report.findings
            if item.check == "No technical jargon in definitions"
        )
        self.assertEqual(finding.level, sbvr_validate.LEVEL_PASS)

    def test_term_inside_a_larger_word_is_not_circular(self) -> None:
        report = sbvr_validate.ValidationReport("fixture.md", "markdown")
        sbvr_validate.validate_vocabulary(
            "## Vocabulary\n\n#### order\n\nA border marker.\n",
            report,
        )

        finding = next(
            item
            for item in report.findings
            if item.check == "No circular definitions"
        )
        self.assertEqual(finding.level, sbvr_validate.LEVEL_PASS)

    def test_main_hides_passing_findings_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "spec.md"
            source.write_text(
                "# Example\n\n"
                "## Vocabulary\n\n#### order\n\nA customer request.\n\n"
                "## Fact Types\n\norder is submitted\n\n"
                "## Rules\n\n**B1:** It is obligatory that an order is submitted.\n",
                encoding="utf-8",
            )
            _, default_output, _ = self.run_main([str(source), "--no-color"])
            _, full_output, _ = self.run_main(
                [str(source), "--no-color", "--show-passing"]
            )

        self.assertNotIn("[PASS]", default_output)
        self.assertIn("[PASS]", full_output)

    def test_text_report_replaces_terminal_control_characters(self) -> None:
        report = sbvr_validate.ValidationReport("bad\x1b[31m\npath", "markdown")
        report.add(
            sbvr_validate.Finding(
                "Unsafe\u202eCategory",
                "Unsafe check",
                sbvr_validate.LEVEL_WARN,
                "bad\x1bmessage",
                evidence=["line\nvalue"],
            )
        )
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            sbvr_validate.print_report(report, use_color=False, show_passing=True)

        output = stdout.getvalue()
        self.assertNotIn("\x1b", output)
        self.assertNotIn("\u202e", output)
        self.assertNotIn("\npath", output)
        self.assertNotIn("line\nvalue", output)

    def test_yaml_requires_non_empty_canonical_sections(self) -> None:
        status, stdout, stderr = self.run_yaml_payload(
            {
                "specification": {
                    "title": "Example",
                    "version": "1.0",
                    "scope": "Example scope",
                },
                "vocabulary": [],
                "fact_types": [],
                "rules": [],
            }
        )

        self.assertEqual(status, 2)
        self.assertFalse(stderr)
        self.assertIn("vocabulary must contain at least one entry", stdout)
        self.assertIn("fact_types must contain at least one entry", stdout)
        self.assertIn("rules must contain at least one entry", stdout)

    def test_yaml_checks_fact_type_references_and_required_fields(self) -> None:
        status, stdout, stderr = self.run_yaml_payload(
            {
                "specification": {
                    "title": "Example",
                    "version": "1.0",
                    "scope": "Example scope",
                },
                "vocabulary": [
                    {
                        "id": "term-order",
                        "term": "order",
                        "definition": "a customer request",
                    }
                ],
                "fact_types": [
                    {
                        "id": "ft-order-is-submitted",
                        "preferred": "order is submitted",
                        "references": ["term-missing"],
                        "quantification": [
                            {
                                "direction": "order to submission",
                                "statement": "each order has one submission state",
                            }
                        ],
                    }
                ],
                "rules": [
                    {
                        "id": "B1",
                        "type": "behavioral",
                        "modality": "obligation",
                        "statement": "It is obligatory that each order is submitted.",
                    }
                ],
            }
        )

        self.assertEqual(status, 2)
        self.assertFalse(stderr)
        self.assertIn("B1: references", stdout)
        self.assertIn("ft-order-is-submitted -> term-missing", stdout)

    def test_accepts_a_minimal_canonical_yaml_spec(self) -> None:
        status, stdout, stderr = self.run_yaml_payload(
            {
                "specification": {
                    "title": "Example",
                    "version": "1.0",
                    "scope": "Example scope",
                },
                "vocabulary": [
                    {
                        "id": "term-request",
                        "term": "request",
                        "definition": "a submitted customer instruction",
                    }
                ],
                "fact_types": [
                    {
                        "id": "ft-customer-submits-request",
                        "preferred": "customer submits request",
                        "references": ["term-request"],
                        "quantification": [
                            {
                                "direction": "customer to request",
                                "statement": "each customer submits zero or more requests",
                            }
                        ],
                    }
                ],
                "rules": [
                    {
                        "id": "B1",
                        "type": "behavioral",
                        "modality": "obligation",
                        "statement": "It is obligatory that each request is reviewed.",
                        "references": ["term-request"],
                    }
                ],
            }
        )

        self.assertEqual(status, 0, stdout)
        self.assertFalse(stderr)
        self.assertIn('"worst_level": "PASS"', stdout)

    def test_yaml_rejects_ad_hoc_fields_and_invalid_quantification(self) -> None:
        status, stdout, stderr = self.run_yaml_payload(
            {
                "specification": {
                    "title": "Example",
                    "version": "1.0",
                    "scope": "Example scope",
                },
                "vocabulary": [
                    {
                        "id": "term-request",
                        "term": "request",
                        "definition": "a submitted customer instruction",
                        "attributes": [],
                    }
                ],
                "fact_types": [
                    {
                        "id": "ft-customer-submits-request",
                        "preferred": "customer submits request",
                        "references": ["term-request", "term-request"],
                        "quantification": [
                            {
                                "direction": "customer to request",
                                "statement": "each customer submits zero or more requests",
                                "minimum": 0,
                            }
                        ],
                    }
                ],
                "rules": [
                    {
                        "id": "B1",
                        "type": "behavioral",
                        "modality": "obligation",
                        "statement": "It is obligatory that each request is reviewed.",
                        "references": ["term-request"],
                    }
                ],
                "format_rationale": "not canonical",
            }
        )

        self.assertEqual(status, 2)
        self.assertFalse(stderr)
        self.assertIn("unexpected top-level keys", stdout)
        self.assertIn("attributes", stdout)
        self.assertIn("minimum", stdout)
        self.assertIn("duplicate ids", stdout)

    def test_yaml_requires_complete_multi_vocabulary_metadata(self) -> None:
        status, stdout, stderr = self.run_yaml_payload(
            {
                "specification": {
                    "title": "Example",
                    "version": "1.0",
                    "scope": "Example scope",
                    "vocabularies": ["sales", "sales"],
                },
                "vocabulary": [
                    {
                        "id": "term-request",
                        "term": "request",
                        "definition": "a submitted customer instruction",
                        "vocabulary": "unknown",
                    }
                ],
                "fact_types": [
                    {
                        "id": "ft-customer-submits-request",
                        "preferred": "customer submits request",
                        "references": ["term-request"],
                        "quantification": [
                            {
                                "direction": "customer to request",
                                "statement": "each customer submits zero or more requests",
                            }
                        ],
                    }
                ],
                "rules": [
                    {
                        "id": "B1",
                        "type": "behavioral",
                        "modality": "obligation",
                        "statement": "It is obligatory that each request is reviewed.",
                        "references": ["term-request"],
                    }
                ],
            }
        )

        self.assertEqual(status, 2)
        self.assertFalse(stderr)
        self.assertIn("contains duplicate names", stdout)

    def test_yaml_reports_mixed_key_types_and_invalid_general_concept(self) -> None:
        status, stdout, stderr = self.run_yaml_payload(
            {
                "specification": {
                    "title": "Example",
                    "version": "1.0",
                    "scope": "Example scope",
                    1: "invalid",
                },
                "vocabulary": [
                    {
                        "id": "term-request",
                        "term": "request",
                        "definition": "a submitted customer instruction",
                        "general_concept": {"invalid": True},
                        2: "invalid",
                    }
                ],
                "fact_types": [
                    {
                        "id": "ft-customer-submits-request",
                        "preferred": "customer submits request",
                        "references": ["term-request"],
                        "quantification": [
                            {
                                "direction": "customer to request",
                                "statement": "each customer submits one request",
                            }
                        ],
                    }
                ],
                "rules": [
                    {
                        "id": "B1",
                        "type": "behavioral",
                        "modality": "obligation",
                        "statement": "It is obligatory that each request is reviewed.",
                        "references": ["term-request"],
                    }
                ],
                3: "invalid",
            }
        )

        self.assertEqual(status, 2)
        self.assertFalse(stderr)
        self.assertIn("unexpected top-level keys", stdout)
        self.assertIn("unexpected specification fields", stdout)
        self.assertIn("general_concept", stdout)


if __name__ == "__main__":
    unittest.main()
