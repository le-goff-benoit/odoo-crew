from odoo.tests.common import TransactionCase


class LabPreparationCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Preparation = cls.env['lab.preparation']

    def make_preparation(self, **values):
        """Créer une demande synthétique indépendante des valeurs calculées."""
        return self.Preparation.create({'name': 'N-17', **values})

    def quantities(self, record):
        """Relire les valeurs métier après invalidation du cache."""
        record.flush_recordset()
        record.invalidate_recordset()
        return (record.ordered_qty, record.delivered_qty, record.prepared_qty,
                record.manual, record.state)
