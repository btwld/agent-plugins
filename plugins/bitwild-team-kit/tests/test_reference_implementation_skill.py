import json
from pathlib import Path
import unittest


SKILL = Path(__file__).resolve().parents[1] / "skills" / "reference-implementation"
REFERENCE_PARSER = "evals/files/reference_parser.dart"
REFERENCE_PARSER_TEST = "evals/files/reference_parser_test.dart"
PARSER_BEFORE = "evals/files/parser_before.dart"
PARSER_FIXTURES = (
    REFERENCE_PARSER,
    REFERENCE_PARSER_TEST,
    PARSER_BEFORE,
    "evals/files/parser_after.dart",
    "evals/files/parser_test.dart",
)


class ReferenceImplementationFixtureTests(unittest.TestCase):
    def test_eval_cases_resolve_the_intended_parser_fixtures(self) -> None:
        payload = json.loads((SKILL / "evals/evals.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["skill_name"], "reference-implementation")
        cases = payload["evals"]
        by_id = {case["id"]: case for case in cases}
        self.assertEqual(len(by_id), len(cases), "Duplicate eval case IDs")
        self.assertEqual(by_id[5]["files"], [REFERENCE_PARSER, REFERENCE_PARSER_TEST])
        self.assertEqual(by_id[6]["files"], [PARSER_BEFORE])

        referenced = {relative for case in cases for relative in case["files"]}
        for relative in PARSER_FIXTURES:
            with self.subTest(fixture=relative):
                self.assertIn(relative, referenced)
                self.assertTrue((SKILL / relative).is_file())
        self.assertTrue((SKILL / "templates/implementation_canvas.md").is_file())

    def test_reference_parser_validates_both_configuration_boundaries(self) -> None:
        parser = (SKILL / REFERENCE_PARSER).read_text(encoding="utf-8")
        self.assertEqual(parser.count("_parseAndValidatePort"), 3)
        for config_type in ("RuntimeConfig", "StoredConfig"):
            with self.subTest(config_type=config_type):
                self.assertEqual(
                    parser.count(f"{config_type}(_parseAndValidatePort(json['port']))"),
                    1,
                )


if __name__ == "__main__":
    unittest.main()
