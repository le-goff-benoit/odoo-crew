from odoo.tests import tagged

from .common import LabRentalCommon
from odoo.addons.lab_rental.models.business import PREPARATION_FEE


@tagged('post_install', '-at_install')
class TestPreparationFee(LabRentalCommon):
    """Décision D-02 du 08/09/2026 : 12 EUR de frais de préparation sur une
    location de quatre jours ou plus, jamais sur un prêt."""

    def test_rental_above_threshold_carries_the_fee(self):
        """CA1 — une location de 5 jours à 10 EUR/jour totalise 50 + 12."""
        rental = self._create_rental("Location 5 jours", days=5, daily_rate=10.0)
        self.assertEqual(rental.amount_total, 62.0)

    def test_rental_at_threshold_carries_the_fee(self):
        """CA2 — la borne de 4 jours est inclusive (Q1)."""
        rental = self._create_rental("Location 4 jours", days=4, daily_rate=10.0)
        self.assertEqual(rental.amount_total, 52.0)

    def test_rental_below_threshold_is_free_of_fee(self):
        """CA3 — sous 4 jours, le total reste jours x tarif."""
        rental = self._create_rental("Location 3 jours", days=3, daily_rate=10.0)
        self.assertEqual(rental.amount_total, 30.0)

    def test_loan_never_carries_the_fee(self):
        """CA4 — un prêt long reste sans frais (Q2)."""
        loan = self._create_rental("Prêt 10 jours", kind='loan', days=10, daily_rate=10.0)
        self.assertEqual(loan.amount_total, 100.0)

    def test_loan_at_threshold_never_carries_the_fee(self):
        """CA5 — la borne inclusive ne rattrape pas les prêts."""
        loan = self._create_rental("Prêt 4 jours", kind='loan', days=4, daily_rate=10.0)
        self.assertEqual(loan.amount_total, 40.0)

    def test_fee_follows_days_and_kind_changes(self):
        """CA6 — le champ stocké suit les changements de durée et de type."""
        rental = self._create_rental("Location évolutive", days=3, daily_rate=10.0)
        self.assertEqual(rental.amount_total, 30.0)

        rental.days = 4
        self.assertEqual(rental.amount_total, 52.0)

        rental.kind = 'loan'
        self.assertEqual(rental.amount_total, 40.0)

        rental.kind = 'rental'
        self.assertEqual(rental.amount_total, 52.0)

    def test_fee_does_not_depend_on_the_daily_rate(self):
        """CA7 — forfait, donc dû même à tarif nul ; et rien à 0 jour."""
        free_rental = self._create_rental("Location 4 jours gratuite", days=4, daily_rate=0.0)
        self.assertEqual(free_rental.amount_total, PREPARATION_FEE)

        empty_rental = self._create_rental("Location 0 jour", days=0, daily_rate=10.0)
        self.assertEqual(empty_rental.amount_total, 0.0)

    def test_fee_is_flat_not_proportional(self):
        """D-02 remplace D-01 : le forfait ne varie pas avec le montant loué."""
        cheap = self._create_rental("Location bon marché", days=4, daily_rate=10.0)
        expensive = self._create_rental("Location chère", days=4, daily_rate=1000.0)
        self.assertEqual(cheap.amount_total - 4 * 10.0, PREPARATION_FEE)
        self.assertEqual(expensive.amount_total - 4 * 1000.0, PREPARATION_FEE)

    def test_stored_value_is_written_in_database(self):
        """Le total est stocké : la valeur doit être lisible en SQL, pas seulement en cache."""
        rental = self._create_rental("Location stockée", days=6, daily_rate=10.0)
        self.env.flush_all()
        self.env.cr.execute("SELECT amount_total FROM lab_rental WHERE id = %s", [rental.id])
        self.assertEqual(self.env.cr.fetchone()[0], 72.0)
