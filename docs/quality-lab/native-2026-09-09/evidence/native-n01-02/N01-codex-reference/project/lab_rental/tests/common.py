from odoo.tests.common import TransactionCase
from odoo.tools import SQL


class LabRentalCommon(TransactionCase):

    def assertStoredTotals(self, records, expected):
        """Vérifier le stockage SQL puis la relecture ORM sans cache."""
        records.flush_recordset(['amount_total'])
        self.env.cr.execute(SQL(
            'SELECT amount_total FROM lab_rental WHERE id IN %s ORDER BY id',
            tuple(records.ids),
        ))
        totals = [row[0] for row in self.env.cr.fetchall()]
        self.assertEqual(len(totals), len(expected))
        for actual, amount in zip(totals, expected):
            self.assertAlmostEqual(actual, amount)
        records.invalidate_recordset(['amount_total'])
        for record, amount in zip(records.sorted('id'), expected):
            self.assertAlmostEqual(record.amount_total, amount)
