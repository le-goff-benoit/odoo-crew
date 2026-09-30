from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import odoo_series  # noqa: E402


def lint(module: Path, series: str, tmp: str) -> str:
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/odoo_lint.py'), '--series', series, str(module)],
                            capture_output=True, text=True,
                            env=dict(os.environ, ODOO_SOURCES_DIR=str(Path(tmp) / 'sources_absentes')))
    return result.stdout


class SeriesDatingTests(unittest.TestCase):
    def test_removed_modules_follow_the_series_of_removal(self):
        self.assertIn('stock_picking_batch', odoo_series.removed_modules('20.0'))
        self.assertIn('base_iban', odoo_series.removed_modules('20.0'))
        self.assertIn('hr_contract', odoo_series.removed_modules('20.0'))
        self.assertNotIn('stock_picking_batch', odoo_series.removed_modules('19.4'))
        self.assertNotIn('base_iban', odoo_series.removed_modules('19.1'))
        self.assertTrue(odoo_series.has('20.0', 'ir_access_csv'))
        self.assertFalse(odoo_series.has('19.0', 'api_ormcache'))

    def test_forms_are_judged_in_their_own_series(self):
        with tempfile.TemporaryDirectory() as tmp:
            module = Path(tmp) / 'quality_series'
            (module / 'models').mkdir(parents=True)
            (module / 'data').mkdir()
            (module / '__manifest__.py').write_text(
                "{'name': 'Fixture', 'version': '20.0.1.0.0', 'license': 'LGPL-3', 'author': 'Test',"
                " 'depends': ['stock_picking_batch'], 'data': ['data/data.xml']}\n")
            (module / 'models/thing.py').write_text(
                'from odoo import api, models\n\n\n'
                'class Thing(models.AbstractModel):\n'
                "    _name = 'quality.thing'\n"
                "    _description = 'Thing'\n"
                "    _rec_names_search = ['name']\n\n"
                "    @api.ormcache('self.env.uid')\n"
                '    def _cached(self):\n'
                '        self.env.registry.clear_cache()\n')
            (module / 'data/data.xml').write_text(
                '<odoo><record id="a" model="ir.attachment">'
                '<field name="datas" type="base64" file="quality_series/static/a.png"/>'
                '</record></odoo>\n')

            recent = lint(module, '20.0', tmp)
            self.assertIn('dépendance `stock_picking_batch` : fusionné dans `stock`', recent)
            self.assertIn('`registry.clear_cache` supprimé en 19.4', recent)
            self.assertIn('`_rec_names_search` s\'écrit en tuple', recent)
            self.assertIn('`type="base64"` remplacé par `type="bytes"`', recent)
            self.assertNotIn("`api.ormcache` n'existe qu'à partir de la 19.4", recent)

            older = lint(module, '19.0', tmp)
            self.assertIn("`api.ormcache` n'existe qu'à partir de la 19.4", older)
            self.assertNotIn('registry.clear_cache', older)
            self.assertNotIn('_rec_names_search', older)
            self.assertNotIn('type="base64"', older)
            self.assertNotIn('stock_picking_batch` : fusionné', older)


if __name__ == '__main__':
    unittest.main()
