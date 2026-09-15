import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from product_model import parse_product
from query_product import query


class QueryProductTests(unittest.TestCase):
    def setUp(self):
        self.path = ROOT / 'assets/examples/product/product.json'
        self.raw = self.path.read_text()
        self.model = parse_product(self.raw)

    def test_cli_stdout_is_json_with_exact_source_records(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/query_product.py'),
                                 str(self.path), 'requirements', '--scope', 'FEAT-WORKFLOW'],
                                capture_output=True, text=True, check=True)
        records = json.loads(result.stdout)
        self.assertEqual({r['id'] for r in records},
                         {'REQ-001', 'REQ-002', 'REQ-003', 'REQ-005', 'REQ-006', 'REQ-008'})
        for record in records:
            self.assertEqual(record, self.model.requirements[record['id']])

    def test_open_questions_filter_preserves_many_to_many_links(self):
        records = query(self.model, 'questions', 'FEAT-REPORT', 'Open')
        self.assertEqual([r['id'] for r in records], ['OQ-001'])
        self.assertEqual(records[0]['requirement_ids'], ['REQ-002', 'REQ-003', 'REQ-004'])
        self.assertEqual(query(self.model, 'questions', 'FEAT-HISTORY', 'Open'), [])

    def test_decisions_and_validations_remain_separate(self):
        self.assertEqual([d['id'] for d in query(self.model, 'decisions', 'MOD-OPS')], ['DEC-001', 'DEC-002'])
        self.assertTrue(all(v['status'] == 'Pending' for v in query(self.model, 'validations', 'MOD-OPS')))
        with self.assertRaisesRegex(ValueError, 'only apply'):
            query(self.model, 'requirements', status='Open')
        with self.assertRaisesRegex(ValueError, 'Unknown scope'):
            query(self.model, 'questions', 'missing')

    def test_scope_records_are_queryable_without_scraping_prds(self):
        self.assertEqual(query(self.model, 'product'), [self.model.product])
        self.assertEqual([r['id'] for r in query(self.model, 'modules')], ['MOD-OPS', 'MOD-REPORT'])
        self.assertEqual([r['id'] for r in query(self.model, 'features', 'MOD-OPS')], ['FEAT-WORKFLOW'])
        self.assertIn('FEAT-HISTORY', [r['id'] for r in query(self.model, 'features')])
        self.assertEqual(query(self.model, 'modules', 'FEAT-WORKFLOW'), [])

    def test_unresolved_includes_assumptions_but_not_answered_questions(self):
        self.assertEqual([q['id'] for q in query(self.model, 'questions', unresolved=True)],
                         ['OQ-001', 'OQ-003'])
        with self.assertRaisesRegex(ValueError, 'mutually exclusive'):
            query(self.model, 'questions', status='Open', unresolved=True)
        with self.assertRaisesRegex(ValueError, 'only apply'):
            query(self.model, 'requirements', unresolved=True)

    def test_cli_unresolved_is_valid_json_and_rejects_conflicting_filters(self):
        command = [sys.executable, str(ROOT / 'scripts/query_product.py'), str(self.path),
                   'questions', '--scope', 'MOD-OPS', '--unresolved']
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertEqual([q['id'] for q in json.loads(result.stdout)], ['OQ-001', 'OQ-003'])
        result = subprocess.run(command + ['--status', 'Open'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_duplicate_json_fields_are_not_silently_overwritten(self):
        for raw in ['{"schema_version": 1, "schema_version": 2}',
                    self.raw.replace('"status": "Open"', '"status": "Answered", "status": "Open"')]:
            with self.assertRaisesRegex(ValueError, 'Duplicate JSON field'):
                parse_product(raw)

    def test_nonstandard_json_constants_are_rejected(self):
        for value in ['NaN', 'Infinity', '-Infinity']:
            with self.assertRaisesRegex(ValueError, 'Invalid JSON constant'):
                parse_product('{"value": ' + value + '}')


if __name__ == '__main__':
    unittest.main()
