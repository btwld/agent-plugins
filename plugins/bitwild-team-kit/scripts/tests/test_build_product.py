import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_product
from product_model import ProductModel


class ProductBuildTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT / 'assets/examples/product/product.json').read_bytes()
        self.data = json.loads(self.raw)

    def test_generated_views_keep_exact_wording_and_scope_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            digest = hashlib.sha256(self.raw).hexdigest()
            paths = build_product.generate(ProductModel(self.data), out, digest)
            self.assertEqual(len(paths), 19)
            workflow = (out / 'prd-FEAT-WORKFLOW.html').read_text()
            report = (out / 'prd-FEAT-REPORT.html').read_text()
            product = (out / 'prd-PROD-OPS.html').read_text()
            for req in self.data['requirements']:
                self.assertIn(req['statement'], product)
            self.assertIn(self.data['requirements'][2]['statement'], workflow)
            self.assertNotIn(self.data['requirements'][3]['statement'], workflow)
            self.assertIn(self.data['requirements'][3]['statement'], report)
            self.assertIn('OQ-001', workflow)
            self.assertIn('OQ-001', report)
            self.assertIn(digest, product)
            markdown = (out / 'prd-MOD-OPS.md').read_text()
            self.assertIn('| --- | --- |', markdown)
            self.assertIn('Acceptance criteria — Proposed', markdown)
            wbs = (out / 'wbs-review.html').read_text()
            self.assertIn('Contributing packages', wbs)
            self.assertIn('TASK-002', wbs)
            self.assertIn('Question dependencies by work stage', wbs)
            self.assertIn('Decision hold', wbs)

    def test_single_question_edit_propagates_to_every_affected_document(self):
        self.data['questions'][0]['text'] = 'Updated shared question'
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            build_product.generate(ProductModel(self.data), out, 'test')
            for name in ['prd-PROD-OPS', 'prd-MOD-OPS', 'prd-MOD-REPORT', 'prd-FEAT-WORKFLOW', 'prd-FEAT-REPORT', 'questions']:
                self.assertIn('Updated shared question', (out / (name + '.html')).read_text())
            self.assertNotIn('Updated shared question', (out / 'prd-FEAT-HISTORY.html').read_text())

    def test_source_text_is_escaped_in_html_and_markdown(self):
        self.data['requirements'][2]['statement'] = '<script>alert(1)</script> | [link](https://example.com)'
        doc = build_product.prd_review(ProductModel(self.data), 'FEAT-WORKFLOW')
        self.assertNotIn('<script>alert', doc.html('test'))
        self.assertIn('&lt;script&gt;', doc.html('test'))
        self.assertNotIn('[link](https://example.com)', doc.markdown_text('test'))
        self.assertIn('\\|', doc.markdown_text('test'))

    def test_regeneration_removes_retired_views_without_deleting_user_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            build_product.generate(ProductModel(self.data), out, 'old')
            (out / 'notes.md').write_text('Keep this')
            self.data['delivery'] = None
            self.data['features'].pop()
            self.data['requirements'].pop(-2)
            build_product.generate(ProductModel(self.data), out, 'new')
            self.assertFalse((out / 'wbs-review.html').exists())
            self.assertFalse((out / 'prd-FEAT-HISTORY.html').exists())
            self.assertEqual((out / 'notes.md').read_text(), 'Keep this')
            self.assertIn('Delivery is not planned', (out / 'traceability.html').read_text())

    def test_invalid_manifest_cannot_delete_files_outside_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'output'
            out.mkdir()
            (Path(tmp) / 'notes.md').write_text('Keep this')
            (out / 'generated-files.json').write_text('["../notes.md"]')
            with self.assertRaisesRegex(ValueError, 'Invalid generated-file manifest'):
                build_product.generate(ProductModel(self.data), out, 'test')
            self.assertEqual((Path(tmp) / 'notes.md').read_text(), 'Keep this')

    def test_cli_rejects_invalid_data_without_creating_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp) / 'bad.json'
            out = Path(tmp) / 'output'
            self.data['requirements'][0]['scope_id'] = 'missing'
            data_path.write_text(json.dumps(self.data))
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/build_product.py'), str(data_path), '--out', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('unknown reference missing', result.stderr)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
