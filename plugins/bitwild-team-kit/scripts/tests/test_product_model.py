import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from product_model import ProductModel


class ProductModelTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'assets/examples/product/product.json').read_text())

    def ids(self, rows):
        return {r['id'] for r in rows}

    def test_product_rollup_counts_unique_requirements(self):
        model = ProductModel(self.data)
        self.assertEqual(len(model.requirements_for('PROD-OPS')), 8)
        self.assertEqual(model.requirements['REQ-003']['statement'],
                         'The system shall retain the history of the operating workflow.')

    def test_feature_selects_shared_and_own_but_not_sibling_requirements(self):
        model = ProductModel(self.data)
        self.assertEqual(self.ids(model.requirements_for('FEAT-WORKFLOW')),
                         {'REQ-001', 'REQ-002', 'REQ-003', 'REQ-005', 'REQ-006', 'REQ-008'})
        self.assertEqual(self.ids(model.requirements_for('FEAT-REPORT')),
                         {'REQ-001', 'REQ-002', 'REQ-004', 'REQ-005', 'REQ-006'})

    def test_module_rollup_includes_child_and_module_owned_requirements(self):
        model = ProductModel(self.data)
        self.assertIn('REQ-008', self.ids(model.requirements_for('MOD-OPS')))
        self.assertIn('REQ-003', self.ids(model.requirements_for('MOD-OPS')))
        self.assertNotIn('REQ-004', self.ids(model.requirements_for('MOD-OPS')))

    def test_ownership_does_not_imply_global_applicability(self):
        model = ProductModel(self.data)
        # Access is product-owned but explicitly applies only to two features.
        self.assertEqual(model.requirements['REQ-002']['scope_id'], 'PROD-OPS')
        self.assertNotIn('REQ-002', self.ids(model.requirements_for('FEAT-HISTORY')))
        self.assertIn('REQ-007', self.ids(model.requirements_for('FEAT-HISTORY')))

    def test_modules_are_optional(self):
        self.data['delivery'] = None
        self.data['modules'] = []
        for feature in self.data['features']:
            feature['parent_id'] = 'PROD-OPS'
        for req in self.data['requirements']:
            if req['scope_id'] == 'MOD-OPS':
                req['scope_id'] = 'FEAT-WORKFLOW'
                req['applies_to'] = ['FEAT-WORKFLOW']
        self.data['questions'][2]['scope_ids'] = ['FEAT-WORKFLOW']
        model = ProductModel(self.data)
        self.assertEqual(len(model.requirements_for('PROD-OPS')), 8)

    def test_prd_does_not_require_a_fabricated_schedule(self):
        self.data['delivery'] = None
        model = ProductModel(self.data)
        self.assertEqual(model.blockers(), [])
        self.assertEqual(model.package_ids_for('REQ-003'), [])
        with self.assertRaisesRegex(ValueError, 'No delivery plan'):
            model.wbs_projection()

    def test_shared_question_changes_once_for_all_affected_views(self):
        self.data['questions'][0]['text'] = 'Shared revision'
        self.data['questions'][0]['status'] = 'Answered'
        self.data['questions'][0]['decision_id'] = 'DEC-001'
        model = ProductModel(self.data)
        for scope in ['PROD-OPS', 'MOD-OPS', 'MOD-REPORT', 'FEAT-WORKFLOW', 'FEAT-REPORT']:
            question = next(q for q in model.questions_for(scope) if q['id'] == 'OQ-001')
            self.assertEqual(question['text'], 'Shared revision')
            self.assertEqual(question['decision_id'], 'DEC-001')
        self.assertNotIn('OQ-001', self.ids(model.questions_for('FEAT-HISTORY')))
        self.assertEqual(model.blockers(), [])
        self.assertEqual(model.validations['VAL-001']['status'], 'Pending')

    def test_assumption_does_not_clear_explicit_blocker(self):
        self.data['questions'][0].update(status='Assumed', decision_id='DEC-002')
        model = ProductModel(self.data)
        self.assertEqual(len(model.blockers()), 2)
        self.data['delivery']['question_dependencies'][1]['blocking'] = False
        self.assertEqual(len(ProductModel(self.data).blockers()), 1)

    def test_resolved_question_needs_a_real_decision_reference(self):
        for status, decision in [('Answered', None), ('Assumed', 'missing'), ('Open', 'DEC-001')]:
            with self.subTest(status=status):
                data = copy.deepcopy(self.data)
                data['questions'][0].update(status=status, decision_id=decision)
                with self.assertRaises(ValueError):
                    ProductModel(data)

    def test_question_can_precede_requirement_definition(self):
        self.data['questions'][0].update(scope_ids=['FEAT-WORKFLOW'], requirement_ids=[])
        model = ProductModel(self.data)
        self.assertIn('OQ-001', self.ids(model.questions_for('FEAT-WORKFLOW')))
        self.assertNotIn('OQ-001', self.ids(model.questions_for('FEAT-REPORT')))

    def test_validation_result_needs_evidence_or_a_waiver(self):
        for status in ['Passed', 'Failed', 'Not required']:
            with self.subTest(status=status):
                data = copy.deepcopy(self.data)
                data['validations'][0]['status'] = status
                with self.assertRaises(ValueError):
                    ProductModel(data)
        self.data['validations'][0].update(status='Passed', evidence_source_ids=['SRC-EXAMPLE'])
        model = ProductModel(self.data)
        self.assertEqual(model.questions['OQ-001']['status'], 'Open')

    def test_completed_task_does_not_pass_validation(self):
        for task in self.data['delivery']['tasks']:
            task['status'] = 'Done'
        model = ProductModel(self.data)
        self.assertEqual(model.validations['VAL-002']['status'], 'Pending')

    def test_primary_coverage_is_unique_without_losing_contributors(self):
        before = copy.deepcopy(self.data)
        model = ProductModel(self.data)
        projection = model.wbs_projection()
        primary = {p['id']: p['requirements'] for p in projection['packages']}
        self.assertIn('REQ-003', primary['2.1'])
        self.assertNotIn('REQ-003', primary['2.2'])
        self.assertEqual(model.package_ids_for('REQ-003'), ['2.1', '2.2'])
        self.assertEqual(sum(len(rids) for rids in primary.values()), 8)
        self.assertEqual(self.data, before)

    def test_missing_duplicate_or_self_contributing_allocation_rejected(self):
        for change in ['missing', 'duplicate', 'self']:
            with self.subTest(change=change):
                data = copy.deepcopy(self.data)
                allocations = data['delivery']['allocations']
                if change == 'missing':
                    allocations.pop()
                elif change == 'duplicate':
                    allocations.append(copy.deepcopy(allocations[0]))
                else:
                    allocations[0]['contributing_package_ids'] = ['1.1']
                with self.assertRaises(ValueError):
                    ProductModel(data)

    def test_task_cannot_claim_unallocated_requirement(self):
        self.data['delivery']['tasks'][0]['requirement_ids'].append('REQ-001')
        with self.assertRaisesRegex(ValueError, 'not allocated'):
            ProductModel(self.data)

    def test_invalid_scope_parent_and_references_rejected(self):
        for change in ['parent', 'source', 'scope', 'duplicate', 'workflow']:
            with self.subTest(change=change):
                data = copy.deepcopy(self.data)
                if change == 'parent':
                    data['features'][0]['parent_id'] = 'FEAT-REPORT'
                elif change == 'source':
                    data['requirements'][0]['source_ids'] = ['missing']
                elif change == 'scope':
                    data['requirements'][0]['applies_to'] = ['missing']
                elif change == 'duplicate':
                    data['requirements'][0]['id'] = 'PROD-OPS'
                else:
                    data['features'][0]['workflow'][0]['requirement_ids'] = ['REQ-004']
                with self.assertRaises(ValueError):
                    ProductModel(data)

    def test_schema_rejects_unknown_keys_statuses_and_malformed_dates(self):
        for change in ['typo', 'status', 'date', 'path']:
            with self.subTest(change=change):
                data = copy.deepcopy(self.data)
                if change == 'typo':
                    data['requirements'][0]['scope'] = 'FEAT-WORKFLOW'
                elif change == 'status':
                    data['questions'][0]['status'] = 'closed-ish'
                elif change == 'date':
                    data['delivery']['start'] = '2026-02-30'
                else:
                    data['features'][0]['id'] = '../../outside'
                with self.assertRaises(ValueError):
                    ProductModel(data)

    def test_undocumented_acceptance_is_explicit_not_filled_with_generic_text(self):
        req = self.data['requirements'][-2]
        self.assertEqual(req['id'], 'REQ-007')
        ProductModel(self.data)
        req['acceptance_status'] = 'Confirmed'
        with self.assertRaisesRegex(ValueError, 'needs criteria'):
            ProductModel(self.data)

    def test_question_dependency_targets_a_real_scheduled_stage(self):
        self.data['delivery']['question_dependencies'][1]['stage_id'] = 'decide'
        with self.assertRaisesRegex(ValueError, 'stage absent'):
            ProductModel(self.data)

    def test_existing_wbs_calendar_checks_still_apply(self):
        self.data['delivery']['packages'][0]['dependencies'] = ['2.1']
        with self.assertRaisesRegex(ValueError, 'cycle'):
            ProductModel(self.data)


if __name__ == '__main__':
    unittest.main()
