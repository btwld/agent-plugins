#!/usr/bin/env python3
"""Regression tests for the ai-slop-review bundled scripts."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "ai-slop-review" / "scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


scope = load("_scope")
slice_mod = load("slice")
sweep = load("sweep")
gate = load("check_findings")

DART_SOURCE = """/// This class manages the counter.
class CounterManager {
  int _count = 0;

  /// The count.
  int get count => _count;

  // Step 1: increment the counter
  void increment() {
    // Note: make sure to increment
    _count++;
  }

  void load() {
    try {
      _count = 1;
    } on Object catch (error) {
      // ignore
    }
  }
}
"""

DART_TEST = """// ignore_for_file: cascade_invocations
import 'package:test/test.dart';

void main() {
  test('should work correctly', () {
    // Arrange
    final a = 1;
    expect(a, a);
  });
  test('does nothing', () {
    final b = 2;
  });
  test('sums like production', () {
    final items = [1, 2];
    expect(sum(items), items.reduce((a, b) => a + b));
  });
}
"""

TS_SOURCE = """// eslint-disable-next-line no-console
export class DataHelper {
  /**
   * @param input the input
   * @returns the output
   */
  run(input: string): string {
    try {
      return input.trim();
    } catch (e) {
      return input; // previously threw
    }
  }
}
"""

PY_SOURCE = """def process_data(data):  # noqa: E501
    # Step 1: validate
    try:
        return data.strip()
    except Exception:
        pass
    # return data
"""

DOC = """# Overview

Welcome! In this section we will explore the powerful, seamless API.
"""


def make_repo(root: Path) -> None:
    (root / "lib").mkdir()
    (root / "test").mkdir()
    (root / "src").mkdir()
    (root / "docs").mkdir()
    (root / "node_modules" / "x").mkdir(parents=True)
    (root / "lib" / "counter.dart").write_text(DART_SOURCE, encoding="utf-8")
    (root / "lib" / "counter.g.dart").write_text("// generated\n", encoding="utf-8")
    (root / "test" / "counter_test.dart").write_text(DART_TEST, encoding="utf-8")
    (root / "src" / "helper.ts").write_text(TS_SOURCE, encoding="utf-8")
    (root / "src" / "tool.py").write_text(PY_SOURCE, encoding="utf-8")
    (root / "docs" / "guide.md").write_text(DOC, encoding="utf-8")
    (root / "node_modules" / "x" / "index.js").write_text("} catch (e) {}\n", encoding="utf-8")
    (root / "analysis_options.yaml").write_text("linter:\n  rules:\n    - prefer_const_constructors\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "init"],
        cwd=root, check=True,
    )


class ScopeTests(unittest.TestCase):
    def test_gather_classifies_and_excludes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            files = scope.gather(root)
            paths = {f.path: f for f in files}
            self.assertIn("lib/counter.dart", paths)
            self.assertEqual(paths["lib/counter.dart"].role, "source")
            self.assertEqual(paths["test/counter_test.dart"].role, "test")
            self.assertEqual(paths["docs/guide.md"].role, "doc")
            self.assertNotIn("lib/counter.g.dart", paths)
            self.assertNotIn("node_modules/x/index.js", paths)
            self.assertNotIn("analysis_options.yaml", paths)

    def test_explicit_file_list_restricts_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            files = scope.gather(root, ["src/helper.ts", "missing.ts"])
            self.assertEqual([f.path for f in files], ["src/helper.ts"])

    def test_test_path_detection(self) -> None:
        self.assertTrue(scope.is_test_path("test/foo_test.dart"))
        self.assertTrue(scope.is_test_path("src/foo.test.ts"))
        self.assertTrue(scope.is_test_path("pkg/tests/test_foo.py"))
        self.assertTrue(scope.is_test_path("src/__tests__/foo.tsx"))
        self.assertFalse(scope.is_test_path("src/testing_utils_readme.ts"))
        self.assertFalse(scope.is_test_path("lib/contest.dart"))


class SliceTests(unittest.TestCase):
    def test_slices_cover_every_file_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            out = root / ".ws"
            code = slice_mod.main(["--root", str(root), "--out", str(out), "--budget", "25"])
            self.assertEqual(code, 0)
            slices = sorted(p.name for p in (out / "slices").glob("*.txt") if p.name != "MANIFEST.txt")
            self.assertEqual(slices, ["A1.txt", "A2.txt", "D1.txt", "T1.txt"])
            manifest = (out / "slices" / "MANIFEST.txt").read_text(encoding="utf-8")
            self.assertIn("C,K", manifest)
            self.assertIn("A1", manifest)
            files = scope.gather(root)
            problems = slice_mod.coverage_problems(files, slice_mod.build_slices(files, 25, 9000, 9000), root)
            self.assertEqual(problems, [])

    def test_large_file_gets_its_own_slice(self) -> None:
        files = [scope.ScopeFile("a.dart", "dart", "source", 50), scope.ScopeFile("b.dart", "dart", "source", 5)]
        slices = slice_mod.cut(files, "A", 10)
        self.assertEqual({k: [f.path for f in v] for k, v in slices.items()}, {"A1": ["a.dart"], "A2": ["b.dart"]})


class SweepTests(unittest.TestCase):
    def run_sweep(self, root: Path, out: Path) -> dict[str, str]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = sweep.main(["--root", str(root), "--out", str(out)])
        self.assertEqual(code, 0)
        return {p.stem: p.read_text(encoding="utf-8") for p in (out / "sweep").glob("*.txt")}

    def test_hit_lists_cover_languages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            lists = self.run_sweep(root, root / ".ws")
            self.assertIn("lib/counter.dart:1:", lists["S1-this-class-docs"])
            self.assertIn("lib/counter.dart:8:", lists["S1-S3-step-narration"])
            self.assertIn("src/tool.py:2:", lists["S1-S3-step-narration"])
            self.assertIn("lib/counter.dart:10:", lists["S3-chat-voice"])
            self.assertIn("lib/counter.dart:17:", lists["S5-catch-all"])
            self.assertIn("src/helper.ts:10:", lists["S5-catch-all"])
            self.assertIn("src/tool.py:5:", lists["S5-catch-all"])
            self.assertIn("src/helper.ts:1:", lists["S12-suppressions"])
            self.assertIn("src/tool.py:1:", lists["S12-suppressions"])
            self.assertIn("test/counter_test.dart:1:", lists["S12-suppressions"])
            self.assertIn("src/helper.ts:4:", lists["S4-tag-style-docs"])
            self.assertIn("src/helper.ts:11:", lists["S2-history-narration"])
            self.assertIn("src/tool.py:7:", lists["S12-commented-out-code"])
            self.assertIn("lib/counter.dart:2:", lists["S9-helper-manager-names"])
            self.assertIn("src/helper.ts:2:", lists["S9-helper-manager-names"])
            self.assertNotIn("node_modules", "".join(lists.values()))

    def test_stale_dart_suppressions_and_test_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            lists = self.run_sweep(root, root / ".ws")
            self.assertIn("cascade_invocations: 1 files", lists["S12-stale-suppressions"])
            hints = lists["hints-ALL"]
            self.assertIn("[S9-S10-marketing-test-name]", hints)
            self.assertIn("[S10-arrange-act-assert]", hints)
            self.assertIn("[S10-tautology]", hints)
            self.assertIn("[S10-computed-expected]", hints)
            self.assertIn("[S10-few-expects] 3 test bodies, 2 assertions", hints)
            self.assertRegex(lists["SUMMARY"], r"\b6\s+hints-ALL")

    def test_hints_follow_test_slices_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            out = root / ".ws"
            with contextlib.redirect_stdout(io.StringIO()):
                slice_mod.main(["--root", str(root), "--out", str(out)])
                sweep.main(["--root", str(root), "--out", str(out)])
            self.assertTrue((out / "sweep" / "hints-T1.txt").is_file())
            self.assertFalse((out / "sweep" / "hints-ALL.txt").exists())


class GateTests(unittest.TestCase):
    def finding(self, **overrides) -> dict:
        base = {
            "id": "C-A1-001", "path": "lib/counter.dart", "start_line": 5, "end_line": 5,
            "pattern": "S1", "severity": "P3", "confidence": "high",
            "snippet": "/// The count.", "guideline": "Effective Dart: AVOID redundancy",
            "why": "Restates the getter name.", "fix": "Delete it.",
        }
        base.update(overrides)
        return base

    def write_finder(self, ws: Path, agent_id: str, findings: list[dict], reviewed: list[dict]) -> Path:
        (ws / "findings").mkdir(parents=True, exist_ok=True)
        path = ws / "findings" / f"{agent_id}.json"
        path.write_text(json.dumps({
            "agent_id": agent_id, "files_reviewed": reviewed, "files_skipped": [],
            "hints_triaged": [], "notes": "", "findings": findings,
        }), encoding="utf-8")
        return path

    def run_gate(self, argv: list[str]) -> tuple[int, str]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = gate.main(argv)
        return code, buffer.getvalue()

    def test_clean_finder_output_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            ws = root / ".ws"
            with contextlib.redirect_stdout(io.StringIO()):
                slice_mod.main(["--root", str(root), "--out", str(ws)])
            reviewed = [{"path": p, "lines_read": scope.count_lines(root / p)}
                        for p in scope.read_file_list(ws / "slices" / "A1.txt")]
            path = self.write_finder(ws, "C-A1", [self.finding()], reviewed)
            code, output = self.run_gate(["--root", str(root), "--workspace", str(ws), str(path)])
            self.assertEqual(code, 0, output)
            self.assertIn("C-A1: 1 findings", output)

    def test_gate_rejects_bad_snippet_lens_and_partial_reads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            ws = root / ".ws"
            with contextlib.redirect_stdout(io.StringIO()):
                slice_mod.main(["--root", str(root), "--out", str(ws)])
            reviewed = [{"path": "lib/counter.dart", "lines_read": 3}]
            findings = [
                self.finding(id="C-A1-001", snippet="/// Not in the file"),
                self.finding(id="C-A1-002", pattern="S5"),
                self.finding(id="C-A1-003", severity="P9", confidence="sure"),
                self.finding(id="C-A1-004", start_line=900, end_line=901),
            ]
            path = self.write_finder(ws, "C-A1", findings, reviewed)
            code, output = self.run_gate(["--root", str(root), "--workspace", str(ws), str(path)])
            self.assertEqual(code, 1)
            self.assertIn("snippet not found", output)
            self.assertIn("pattern S5 not in lens C", output)
            self.assertIn("bad severity P9", output)
            self.assertIn("bad confidence sure", output)
            self.assertIn("end_line 901 > file length", output)
            self.assertIn("lines_read 3 !=", output)
            self.assertIn("not reviewed: src/helper.ts", output)

    def test_no_slices_mode_and_diff_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            # Change lines 8-11 of the Dart file on a branch so the diff range is meaningful.
            target = root / "lib" / "counter.dart"
            lines = target.read_text(encoding="utf-8").split("\n")
            lines[7] = "  // Step 1: bump the counter"
            target.write_text("\n".join(lines), encoding="utf-8")
            ws = root / ".ws"
            findings = [
                self.finding(id="C-X-001", start_line=8, end_line=8, snippet="// Step 1: bump the counter", pattern="S3"),
                self.finding(id="C-X-002", start_line=5, end_line=5),
                self.finding(id="C-X-003", start_line=5, end_line=5, preexisting=True),
            ]
            path = self.write_finder(ws, "C-X", findings, [])
            code, output = self.run_gate(["--root", str(root), "--no-slices", "--diff-range", "HEAD", str(path)])
            self.assertEqual(code, 1)
            self.assertIn("C-X-002: outside the diff", output)
            self.assertNotIn("C-X-001:", output)
            self.assertNotIn("C-X-003:", output)

    def test_validation_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            ws = root / ".ws"
            self.write_finder(ws, "C-A1", [self.finding(id="C-A1-001"), self.finding(id="C-A1-002", start_line=1, end_line=1, snippet="/// This class manages the counter.")], [])
            (ws / "validations").mkdir()
            validation = ws / "validations" / "VC-1.json"
            validation.write_text(json.dumps({
                "agent_id": "VC-1", "inputs": ["C-A1"],
                "reviews": [
                    {"finding_id": "C-A1-001", "verdict": "confirm", "reason": "Line 5 restates `count`."},
                    {"finding_id": "C-A1-002", "verdict": "downgrade", "reason": "House style."},
                ],
                "missed": [self.finding(id="VC-1-M1", pattern="S5", start_line=17, end_line=17,
                                        snippet="} on Object catch (error) {", lens="K", severity="P2")],
            }), encoding="utf-8")
            code, output = self.run_gate(["--root", str(root), "--workspace", str(ws), "--validation", str(validation)])
            self.assertEqual(code, 1)
            self.assertIn("downgrade without a valid new severity", output)
            self.assertNotIn("no verdict", output)
            self.assertNotIn("VC-1 missed", output)
            self.assertIn("'confirm': 1", output)


if __name__ == "__main__":
    unittest.main()
