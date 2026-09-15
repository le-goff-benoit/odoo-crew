from unittest.mock import patch

from odoo.tests import tagged

from .common import LabPreparationCommon


@tagged('post_install', '-at_install')
class TestLabPreparation(LabPreparationCommon):
    def test_cron_mixed_and_replay(self):
        """N-17 : solde borné, saisies et terminés préservés, rejeu stable."""
        records = self.Preparation.create([
            {'name': 'auto', 'ordered_qty': 10, 'delivered_qty': 3, 'prepared_qty': 999},
            {'name': 'over', 'ordered_qty': 3, 'delivered_qty': 5, 'prepared_qty': 999},
            {'name': 'equal', 'ordered_qty': 3, 'delivered_qty': 3, 'prepared_qty': 999},
            {'name': 'zero', 'ordered_qty': 10, 'manual': True},
            {'name': 'partial', 'ordered_qty': 10, 'prepared_qty': 2, 'manual': True},
            {'name': 'done', 'ordered_qty': 10, 'prepared_qty': 88, 'state': 'done'},
            {'name': 'done manual', 'ordered_qty': 10, 'prepared_qty': 4,
             'manual': True, 'state': 'done'},
        ])
        before = records.read(['name', 'ordered_qty', 'delivered_qty', 'manual', 'state', 'parent_id'])
        self.Preparation._cron_prepare()
        self.assertEqual(records.mapped('prepared_qty'), [7, 0, 0, 0, 2, 88, 4])
        self.assertEqual(records.read(list(before[0].keys())), before)
        with patch.object(type(self.Preparation), 'write', autospec=True) as write:
            self.Preparation._cron_prepare()
            write.assert_not_called()

    def test_manual_zero_then_cron(self):
        """Zéro est une saisie, même après une préparation automatique."""
        manual = self.make_preparation(ordered_qty=10, delivered_qty=3, prepared_qty=7)
        automatic = self.make_preparation(ordered_qty=12, delivered_qty=2)
        self.assertTrue(manual.action_set_manual(0))
        self.assertEqual(self.quantities(manual), (10, 3, 0, True, 'draft'))
        self.Preparation._cron_prepare()
        self.assertEqual(self.quantities(manual), (10, 3, 0, True, 'draft'))
        self.assertEqual(automatic.prepared_qty, 10)

    def test_manual_nonzero_then_cron(self):
        """Une saisie explicite est conservée sans arrondi ajouté."""
        record = self.make_preparation(ordered_qty=10, delivered_qty=3)
        record.action_set_manual(2.125)
        self.Preparation._cron_prepare()
        self.assertEqual(self.quantities(record), (10, 3, 2.125, True, 'draft'))

    def test_copy_then_cron(self):
        """La duplication ouvre une nouvelle demande, sans quantités héritées."""
        source = self.make_preparation(ordered_qty=10, delivered_qty=3,
                                       prepared_qty=2, manual=True, state='done')
        duplicate = source.copy()
        self.assertEqual(self.quantities(duplicate), (10, 0, 0, False, 'draft'))
        self.Preparation._cron_prepare()
        self.assertEqual(self.quantities(duplicate), (10, 0, 10, False, 'draft'))
        self.assertEqual(self.quantities(source), (10, 3, 2, True, 'done'))

    def test_remainder_then_cron(self):
        """Le reliquat porte le solde ; la source est figée avec sa saisie."""
        source = self.make_preparation(ordered_qty=10, delivered_qty=3,
                                       prepared_qty=2, manual=True)
        count = self.Preparation.search_count([])
        remainder = source.action_remainder()
        self.assertEqual(len(remainder), 1)
        self.assertEqual(self.Preparation.search_count([]), count + 1)
        self.assertEqual(remainder.parent_id, source)
        self.assertEqual(self.quantities(remainder), (7, 0, 0, False, 'draft'))
        self.assertEqual(self.quantities(source), (10, 3, 2, True, 'done'))
        for _ in range(2):
            self.Preparation._cron_prepare()
            self.assertEqual(self.quantities(remainder), (7, 0, 7, False, 'draft'))
            self.assertEqual(self.quantities(source), (10, 3, 2, True, 'done'))

    def test_remainder_without_positive_balance(self):
        """Une égalité ou une surlivraison ne crée aucune demande."""
        for delivered in (10, 12):
            with self.subTest(delivered=delivered):
                source = self.make_preparation(ordered_qty=10, delivered_qty=delivered,
                                               prepared_qty=2, manual=True)
                before = source.read()[0]
                count = self.Preparation.search_count([])
                result = source.action_remainder()
                self.assertEqual(result, self.Preparation.browse())
                self.assertEqual(self.Preparation.search_count([]), count)
                self.assertEqual(source.read()[0], before)

    def test_remainder_singleton(self):
        """Les appels vide et multiple échouent avant toute écriture."""
        records = self.make_preparation(ordered_qty=10) | self.make_preparation(ordered_qty=5)
        before = self.Preparation.search([]).read()
        for selection in (self.Preparation.browse(), records):
            with self.assertRaisesRegex(ValueError, 'Expected singleton'):
                selection.action_remainder()
        self.assertEqual(self.Preparation.search([]).read(), before)

    def test_sub_cent_balance(self):
        """Ni cron ni reliquat n'arrondissent un petit solde positif à zéro."""
        source = self.make_preparation(ordered_qty=1.003, delivered_qty=1)
        self.Preparation._cron_prepare()
        self.assertAlmostEqual(source.prepared_qty, 0.003)
        remainder = source.action_remainder()
        self.assertAlmostEqual(remainder.ordered_qty, 0.003)
        self.Preparation._cron_prepare()
        self.assertAlmostEqual(remainder.prepared_qty, 0.003)
        self.assertAlmostEqual(source.prepared_qty, 0.003)

    def test_ir_cron_execution(self):
        """Exécuter le vrai canal ir.cron sur un jeu mixte transactionnel."""
        automatic = self.make_preparation(ordered_qty=10, delivered_qty=3, prepared_qty=999)
        manual = self.make_preparation(ordered_qty=10, manual=True)
        done = self.make_preparation(ordered_qty=10, prepared_qty=88, state='done')
        cron = self.env['ir.cron'].create({
            'name': 'N-17 test',
            'model_id': self.env['ir.model']._get_id('lab.preparation'),
            'state': 'code',
            'code': 'model._cron_prepare()',
        })
        with self.enter_registry_test_mode():
            self.assertTrue(cron.method_direct_trigger())
        self.assertEqual(self.quantities(automatic), (10, 3, 7, False, 'draft'))
        self.assertEqual(self.quantities(manual), (10, 0, 0, True, 'draft'))
        self.assertEqual(self.quantities(done), (10, 0, 88, False, 'done'))
