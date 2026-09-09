from odoo.tests import tagged

from .common import LabRentalCommon
from odoo.addons.lab_rental.models.business import (
    PREPARATION_FEE,
    PREPARATION_FEE_MIN_DAYS,
)


@tagged('post_install', '-at_install')
class TestPreparationFee(LabRentalCommon):
    """Règle tarifaire D-03 (decisions/2026-09-09.md), critères CA1 à CA10.

    D-03 remplace D-02 : le forfait passe de 12 à 15 EUR et le seuil de 4 à 5 jours.
    Les attentes sont écrites en clair, valeur par valeur : c'est ce qui a rendu la
    bascule de règle visible plutôt que silencieuse.
    """

    def test_rental_at_threshold_pays_the_fee(self):
        """CA1 — la borne des 5 jours est inclusive."""
        rental = self._create_rental(5)
        self.assertEqual(rental.amount_total, 65.0)

    def test_rental_at_former_threshold_pays_no_fee(self):
        """CA2 — 4 jours ne paie plus rien : l'ancien seuil de D-02 est mort."""
        rental = self._create_rental(4)
        self.assertEqual(rental.amount_total, 40.0)

    def test_rental_below_threshold_pays_no_fee(self):
        """CA3 — sous le seuil, le total reste jours * tarif."""
        rental = self._create_rental(3)
        self.assertEqual(rental.amount_total, 30.0)

    def test_rental_above_threshold_pays_the_fee_once(self):
        """CA4 — le forfait est fixe par location, il ne se multiplie pas par les jours."""
        rental = self._create_rental(10)
        self.assertEqual(rental.amount_total, 115.0)

    def test_loan_at_threshold_pays_no_fee(self):
        """CA5 — un prêt de 5 jours reste sans frais."""
        loan = self._create_rental(5, kind='loan')
        self.assertEqual(loan.amount_total, 50.0)

    def test_loan_above_threshold_pays_no_fee(self):
        """CA6 — un prêt long reste sans frais."""
        loan = self._create_rental(10, kind='loan')
        self.assertEqual(loan.amount_total, 100.0)

    def test_fee_follows_days_and_kind_changes(self):
        """CA7 — le total stocké suit les changements de durée puis de nature."""
        rental = self._create_rental(PREPARATION_FEE_MIN_DAYS - 1)
        self.assertEqual(rental.amount_total, 40.0)

        rental.days = PREPARATION_FEE_MIN_DAYS
        self.assertEqual(rental.amount_total, 50.0 + PREPARATION_FEE)

        rental.kind = 'loan'
        self.assertEqual(rental.amount_total, 50.0)

    def test_empty_rental_totals_zero(self):
        """CA8 — une location vide ne déclenche pas le forfait."""
        rental = self._create_rental(0, daily_rate=0.0)
        self.assertEqual(rental.amount_total, 0.0)

    def test_amount_total_is_stored_in_database(self):
        """CA9 — la valeur est bien en base, pas recalculée à la lecture."""
        rental = self._create_rental(5)
        self.env.flush_all()
        self.env.cr.execute(
            "SELECT amount_total FROM lab_rental WHERE id = %s", [rental.id],
        )
        self.assertEqual(self.env.cr.fetchone()[0], 65.0)

    def test_rule_constants_match_the_decision(self):
        """Garde-fou : les constantes du module portent bien les valeurs de D-03.

        Sans ce test, remonter le seuil sans remonter le montant (ou l'inverse)
        passerait à travers les cas chiffrés qui se recoupent.
        """
        self.assertEqual(PREPARATION_FEE, 15.0)
        self.assertEqual(PREPARATION_FEE_MIN_DAYS, 5)

    def test_negative_days_stay_below_threshold(self):
        """Cas limite hors D-03 : une durée négative ne peut pas franchir le seuil."""
        rental = self._create_rental(-5)
        self.assertEqual(rental.amount_total, -50.0)
