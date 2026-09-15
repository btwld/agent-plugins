import copy
import importlib.util
import json
from pathlib import Path
import unittest
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('build_wbs', ROOT / 'scripts/build_wbs.py')
wbs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wbs)


class WbsTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'assets/examples/wbs/plan.json').read_text())

    def test_example_complete_coverage(self):
        maps, assigned = wbs.validate(self.data)
        self.assertEqual(set(assigned), set(maps['requirements']))
        self.assertEqual(assigned['REQ-007'], '4.1')

    def test_unknown_duplicate_and_missing_requirements(self):
        for replacement in [['REQ-001'], ['NO-SUCH-ID'], []]:
            with self.subTest(replacement=replacement):
                data = copy.deepcopy(self.data)
                data['packages'][1]['requirements'] = replacement
                with self.assertRaises(ValueError):
                    wbs.validate(data)

    def test_duplicate_ids(self):
        self.data['groups'].append(copy.deepcopy(self.data['groups'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate ID'):
            wbs.validate(self.data)

    def test_noncurrent_scope_cannot_be_scheduled(self):
        self.data['packages'][-1]['stages'] = self.data['packages'][0]['stages']
        with self.assertRaisesRegex(ValueError, 'unscheduled'):
            wbs.validate(self.data)

    def test_dependency_cycle(self):
        self.data['packages'][0]['dependencies'] = ['2.1']
        with self.assertRaisesRegex(ValueError, 'cycle'):
            wbs.validate(self.data)

    def test_finish_to_start_boundary(self):
        wbs.validate(self.data)
        self.data['packages'][1]['stages'][-1]['end'] = '2026-10-27'
        with self.assertRaisesRegex(ValueError, 'before dependency'):
            wbs.validate(self.data)

    def test_gate_before_prerequisite(self):
        self.data['milestones'][1]['date'] = '2026-11-11'
        with self.assertRaisesRegex(ValueError, 'gate precedes'):
            wbs.validate(self.data)

    def test_stage_order_and_overlap(self):
        for key, value in [('stage', 'verify'), ('end', '2026-10-10')]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.data)
                data['packages'][0]['stages'][0][key] = value
                with self.assertRaises(ValueError):
                    wbs.validate(data)

    def test_references_and_disposition(self):
        for field, value in [('group', 'unknown'), ('release', 'unknown'), ('disposition', 'Deferred'), ('dependencies', ['unknown'])]:
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data['packages'][0][field] = value
                with self.assertRaises(ValueError):
                    wbs.validate(data)

    def test_date_window(self):
        self.data['packages'][0]['stages'][0]['start'] = '2026-09-30'
        with self.assertRaisesRegex(ValueError, 'outside project'):
            wbs.validate(self.data)

    def test_render_escapes_content(self):
        self.data['project']['name'] = '<script>alert(1)</script>'
        maps, assigned = wbs.validate(self.data)
        html = wbs.render(self.data, maps, assigned, 'test')
        self.assertNotIn('<script>alert', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn(self.data['requirements'][0]['statement'], html)

    def test_long_timeline_splits_into_windows(self):
        self.data['project']['end'] = '2027-03-01'
        maps, _ = wbs.validate(self.data)
        self.assertEqual(wbs.timeline(self.data, maps).count('class="timeline"'), 2)


if __name__ == '__main__':
    unittest.main()
