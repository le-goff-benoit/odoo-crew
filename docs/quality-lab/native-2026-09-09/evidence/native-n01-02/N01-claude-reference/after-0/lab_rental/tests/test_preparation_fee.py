from odoo.tests import tagged

from .common import LabRentalCommon
from odoo.addons.lab_rental.models.business import (
    PREPARATION_FEE,
    PREPARATION_FEE_MIN_DAYS,
)


@tagged('post_install', '-at_install')
class TestPreparationFee(LabRentalCommon):
    """Règle tarifaire D-02 (decisions/2026-09-08.md), critères CA1 à CA8."""

    def test_rental_at_threshold_pays_the_fee(self):
        """CA1 — la borne des 4 jours est inclusive (Q1)."""
        rental = self._create_rental(4)
        self.assertEqual(rental.amount_total, 52.0)

    def test_rental_below_threshold_pays_no_fee(self):
        """CA2 — sous le seuil, le total reste jours * tarif."""
        rental = self._create_rental(3)
        self.assertEqual(rental.amount_total, 30.0)

    def test_rental_above_threshold_pays_the_fee_once(self):
        """CA3 — le forfait est fixe par location, il ne se multiplie pas par les jours."""
        rental = self._create_rental(10)
        self.assertEqual(rental.amount_total, 112.0)

    def test_loan_at_threshold_pays_no_fee(self):
        """CA4 — un prêt de 4 jours reste sans frais (Q2)."""
        loan = self._create_rental(4, kind='loan')
        self.assertEqual(loan.amount_total, 40.0)

    def test_loan_above_threshold_pays_no_fee(self):
        """CA5 — un prêt long reste sans frais."""
        loan = self._create_rental(10, kind='loan')
        self.assertEqual(loan.amount_total, 100.0)

    def test_fee_follows_days_and_kind_changes(self):
        """CA6 — le total stocké suit les changements de durée puis de nature."""
        rental = self._create_rental(3)
        self.assertEqual(rental.amount_total, 30.0)

        rental.days = PREPARATION_FEE_MIN_DAYS
        self.assertEqual(rental.amount_total, 40.0 + PREPARATION_FEE)

        rental.kind = 'loan'
        self.assertEqual(rental.amount_total, 40.0)

    def test_empty_rental_totals_zero(self):
        """CA7 — une location vide ne déclenche pas le forfait."""
        rental = self._create_rental(0, daily_rate=0.0)
        self.assertEqual(rental.amount_total, 0.0)

    def test_amount_total_is_stored_in_database(self):
        """CA8 — la valeur est bien en base, pas recalculée à la lecture."""
        rental = self._create_rental(4)
        self.env.flush_all()
        self.env.cr.execute(
            "SELECT amount_total FROM lab_rental WHERE id = %s", [rental.id],
        )
        self.assertEqual(self.env.cr.fetchone()[0], 52.0)

    def test_negative_days_stay_below_threshold(self):
        """Cas limite hors D-02 : une durée négative ne peut pas franchir le seuil."""
        rental = self._create_rental(-5)
        self.assertEqual(rental.amount_total, -50.0)
