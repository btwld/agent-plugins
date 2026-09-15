import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    'design-kit': {'design-system', 'image-to-code', 'accessibility-review', 'design-verification', 'frontend-design', 'ux-copy', 'visual-exploration', 'design-critique', 'user-research', 'url-to-code'},
    'product-kit': {'product-brainstorming', 'research-synthesis',
                    'competitive-brief', 'ux-friction-research', 'write-prd', 'write-wbs'},
    'engineering-kit': {'adversarial-change-review', 'ai-slop-review', 'architecture',
                        'clean-sheet-review', 'code-simplifier', 'executing-plans',
                        'pull-request-authoring', 'reference-implementation', 'sbvr',
                        'webapp-verification', 'writing-plans'},
}


class PackagingTests(unittest.TestCase):
    def test_catalogs_resolve_the_same_plugins(self):
        codex = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())
        claude = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        self.assertEqual(codex['name'], claude['name'])
        a = {p['name']: p['source']['path'] for p in codex['plugins']}
        b = {p['name']: p['source'] for p in claude['plugins']}
        self.assertEqual(a, b)
        self.assertEqual(set(a), set(SKILLS))
        self.assertEqual(len(a), len(codex['plugins']))
        self.assertEqual(len(b), len(claude['plugins']))
        self.assertEqual({p.name for p in (ROOT / 'plugins').iterdir()}, set(SKILLS))
        for name, path in a.items():
            self.assertEqual((ROOT / path).name, name)
            self.assertTrue((ROOT / path).is_dir())

    def test_manifest_metadata_and_shared_skills_do_not_drift(self):
        for plugin in (ROOT / 'plugins').iterdir():
            codex = json.loads((plugin / '.codex-plugin/plugin.json').read_text())
            claude = json.loads((plugin / '.claude-plugin/plugin.json').read_text())
            for key in ['name', 'version', 'description', 'author', 'repository', 'skills']:
                self.assertEqual(codex[key], claude[key], (plugin.name, key))
            self.assertEqual(codex['name'], plugin.name)
            self.assertNotIn('+codex.', codex['version'])
            self.assertEqual({p.parent.name for p in (plugin / 'skills').glob('*/SKILL.md')},
                             SKILLS[plugin.name])
        names = [p.parent.name for p in (ROOT / 'plugins').glob('*/skills/*/SKILL.md')]
        self.assertEqual(len(names), len(set(names)), 'Duplicate skill owners')

    def test_runtime_resources_stay_inside_plugin(self):
        for plugin in (ROOT / 'plugins').iterdir():
            for p in plugin.rglob('*'):
                if '__pycache__' in p.parts:
                    continue
                self.assertTrue(p.resolve().is_relative_to(plugin.resolve()))
                if p.suffix != '.md' or p == plugin / 'README.md':
                    continue
                for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
                    if target.startswith(('https:', 'http:', '#')):
                        continue
                    resolved = (p.parent / target.split('#')[0]).resolve()
                    self.assertTrue(resolved.exists(), (p, target))
                    self.assertTrue(resolved.is_relative_to(plugin.resolve()), (p, target))

    def test_product_example_resolves_its_bundled_schema(self):
        plugin = ROOT / 'plugins/product-kit'
        example = plugin / 'assets/examples/product/product.json'
        resolved = (example.parent / json.loads(example.read_text())['$schema']).resolve()
        self.assertEqual(resolved, (plugin / 'references/product.schema.json').resolve())


if __name__ == '__main__':
    unittest.main()
