#!/usr/bin/env python3
"""Regression tests for the SBVR renumbering helper."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "sbvr"
    / "scripts"
    / "renumber.py"
)
SPEC = importlib.util.spec_from_file_location("sbvr_renumber", SCRIPT)
assert SPEC and SPEC.loader
sbvr_renumber = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sbvr_renumber)


class SbvrRenumberTests(unittest.TestCase):
    def test_rewrites_headings_and_prose_but_preserves_code(self) -> None:
        original = (
            "**B4:** It is obligatory that the buyer pays.\n"
            "See B4 and `B4` for context.\n\n"
            "```text\n"
            "**B4:** This example is not a rule.\n"
            "See B4 in the example.\n"
            "```\n"
        )

        rewritten, mapping = sbvr_renumber.renumber(original)

        self.assertEqual(mapping, {"B4": "B1"})
        self.assertIn("**B1:**", rewritten)
        self.assertIn("See B1 and `B4`", rewritten)
        self.assertIn("**B4:** This example is not a rule.", rewritten)
        self.assertIn("See B4 in the example.", rewritten)

    def test_rejects_duplicate_rule_headings(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate rule heading: B4"):
            sbvr_renumber.renumber(
                "**B4:** First rule.\n\n**B4:** Duplicate rule.\n"
            )

    def test_ignores_inline_code_and_midline_bold_examples(self) -> None:
        original = (
            "Use `**B99:**` as an implementation example.\n"
            "The text **B88:** is not a rule heading.\n\n"
            "**B4:** It is obligatory that the buyer pays.\n"
            "- **D7:** It is necessary that each buyer has one identifier.\n"
        )

        rewritten, mapping = sbvr_renumber.renumber(original)

        self.assertEqual(mapping, {"B4": "B1", "D7": "D1"})
        self.assertIn("`**B99:**`", rewritten)
        self.assertIn("The text **B88:**", rewritten)
        self.assertIn("**B1:**", rewritten)
        self.assertIn("- **D1:**", rewritten)

    def test_preserves_markdown_link_destinations(self) -> None:
        original = (
            "**B4:** It is obligatory that the buyer pays.\n"
            "See [B4](https://example.test/rules/B4), "
            "<https://example.test/B4>, and [B4].\n"
            "[B4]: rules/B4.md\n"
        )

        rewritten, mapping = sbvr_renumber.renumber(original)

        self.assertEqual(mapping, {"B4": "B1"})
        self.assertIn("[B1](https://example.test/rules/B4)", rewritten)
        self.assertIn("<https://example.test/B4>", rewritten)
        self.assertIn("and [B1].", rewritten)
        self.assertIn("[B1]: rules/B4.md", rewritten)

    def test_preserves_bare_url_destinations(self) -> None:
        original = (
            "**B4:** It is obligatory that the buyer pays.\n"
            "See B4 at https://example.test/rules/B4.\n"
        )

        rewritten, mapping = sbvr_renumber.renumber(original)

        self.assertEqual(mapping, {"B4": "B1"})
        self.assertIn("See B1 at https://example.test/rules/B4.", rewritten)

    def test_inline_code_prefix_does_not_create_a_rule_heading(self) -> None:
        original = (
            "`sample` **B4:** This text is not a rule heading.\n"
            "**B7:** It is obligatory that the buyer pays.\n"
        )

        rewritten, mapping = sbvr_renumber.renumber(original)

        self.assertEqual(mapping, {"B7": "B1"})
        self.assertIn("`sample` **B4:**", rewritten)
        self.assertIn("**B1:**", rewritten)

    def test_rejects_non_markdown_input_without_changing_it(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "rules.txt"
            original = "**B4:** Rule.\n"
            source.write_text(original, encoding="utf-8")
            old_argv = sbvr_renumber.sys.argv
            try:
                sbvr_renumber.sys.argv = [str(SCRIPT), str(source)]
                with contextlib.redirect_stderr(io.StringIO()):
                    status = sbvr_renumber.main()
            finally:
                sbvr_renumber.sys.argv = old_argv

            self.assertEqual(status, 1)
            self.assertEqual(source.read_text(encoding="utf-8"), original)

    def test_rejects_symlinked_input_without_changing_its_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "target.md"
            target.write_text("**B4:** Rule.\n", encoding="utf-8")
            source = root / "rules.md"
            source.symlink_to(target)
            old_argv = sbvr_renumber.sys.argv
            try:
                sbvr_renumber.sys.argv = [str(SCRIPT), str(source)]
                with contextlib.redirect_stderr(io.StringIO()):
                    status = sbvr_renumber.main()
            finally:
                sbvr_renumber.sys.argv = old_argv

            self.assertEqual(status, 1)
            self.assertEqual(target.read_text(encoding="utf-8"), "**B4:** Rule.\n")

    def test_error_path_renders_terminal_controls(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = Path(raw) / "bad\u202ename.txt"
            source.write_text("**B4:** Rule.\n", encoding="utf-8")
            old_argv = sbvr_renumber.sys.argv
            try:
                sbvr_renumber.sys.argv = [str(SCRIPT), str(source)]
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    status = sbvr_renumber.main()
            finally:
                sbvr_renumber.sys.argv = old_argv

        self.assertEqual(status, 1)
        self.assertIn(r"bad\u202ename.txt", stderr.getvalue())
        self.assertNotIn("\u202e", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
