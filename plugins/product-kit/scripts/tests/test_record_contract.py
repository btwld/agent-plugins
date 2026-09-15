import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from product_model import ProductModel


class RecordContractTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'assets/examples/product/product.json').read_text())
        self.schema = json.loads((ROOT / 'references/product.schema.json').read_text())
        self.validator = Draft202012Validator(self.schema)

    def test_schema_rejects_inconsistent_question_states_and_missing_targets(self):
        Draft202012Validator.check_schema(self.schema)
        self.assertTrue(self.validator.is_valid(self.data))
        for update in [dict(status='Open', decision_id='DEC-001'),
                       dict(status='Answered', decision_id=None),
                       dict(status='Assumed', decision_id=None),
                       dict(scope_ids=[], requirement_ids=[])]:
            with self.subTest(update=update):
                data = copy.deepcopy(self.data)
                data['questions'][0].update(update)
                self.assertFalse(self.validator.is_valid(data))
                with self.assertRaises(ValueError):
                    ProductModel(data)

    def test_reference_validation_still_required_beyond_json_schema(self):
        self.data['questions'][0].update(status='Answered', decision_id='DEC-MISSING')
        self.assertTrue(self.validator.is_valid(self.data))
        with self.assertRaisesRegex(ValueError, 'unknown reference DEC-MISSING'):
            ProductModel(self.data)

    def test_both_builders_reject_ambiguous_json_before_writing(self):
        product = json.dumps(self.data)
        wbs = (ROOT / 'assets/examples/wbs/plan.json').read_text()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for script, raw in [('build_product.py', product), ('build_wbs.py', wbs)]:
                for bad in ['{"ignored": NaN,' + raw[1:],
                            '{"ignored": 1,"ignored": 2,' + raw[1:]]:
                    with self.subTest(script=script, bad=bad[:45]):
                        source = root / 'input.json'
                        source.write_text(bad)
                        out = root / 'output'
                        result = subprocess.run([sys.executable, str(ROOT / 'scripts' / script),
                                                 str(source), '--out', str(out)],
                                                capture_output=True, text=True)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertRegex(result.stderr, 'Invalid JSON constant|Duplicate JSON field')
                        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
