from odoo.tests import TransactionCase


class LabRentalCommon(TransactionCase):
    """Socle des tests de lab_rental : un tarif de référence et un raccourci de création."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.daily_rate = 10.0

    def _create_rental(self, days, kind='rental', daily_rate=None):
        return self.env['lab.rental'].create({
            'name': f"{kind} {days}j",
            'days': days,
            'kind': kind,
            'daily_rate': self.daily_rate if daily_rate is None else daily_rate,
        })
