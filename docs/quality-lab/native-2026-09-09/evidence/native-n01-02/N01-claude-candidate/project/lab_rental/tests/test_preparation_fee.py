from odoo.tests import tagged

from .common import LabRentalCommon
from odoo.addons.lab_rental.models.business import (
    PREPARATION_FEE,
    PREPARATION_FEE_MIN_DAYS,
)


@tagged('post_install', '-at_install')
class TestPreparationFee(LabRentalCommon):
    """Décision D-03 du 09/09/2026 : 15 EUR de frais de préparation sur une
    location de cinq jours ou plus, jamais sur un prêt.

    D-03 remplace D-02 (12 EUR dès quatre jours) : les cas de la borne à quatre
    jours sont conservés ici, mais avec l'attente inverse — ils vérifient
    désormais l'**absence** de frais. C'est le sens du changement, pas un oubli."""

    def test_rental_above_threshold_carries_the_fee(self):
        """CA1 — une location de 5 jours à 10 EUR/jour totalise 50 + 15."""
        rental = self._create_rental("Location 5 jours", days=5, daily_rate=10.0)
        self.assertEqual(rental.amount_total, 65.0)

    def test_rental_at_former_threshold_is_free_of_fee(self):
        """CA2 — à quatre jours, D-03 ne prélève plus rien (D-02 prélevait 12)."""
        rental = self._create_rental("Location 4 jours", days=4, daily_rate=10.0)
        self.assertEqual(rental.amount_total, 40.0)

    def test_rental_well_above_threshold_carries_the_fee(self):
        """CA3 — une location de 6 jours à 10 EUR/jour totalise 60 + 15."""
        rental = self._create_rental("Location 6 jours", days=6, daily_rate=10.0)
        self.assertEqual(rental.amount_total, 75.0)

    def test_rental_below_threshold_is_free_of_fee(self):
        """CA2 (bis) — sous le seuil, le total reste jours x tarif."""
        rental = self._create_rental("Location 3 jours", days=3, daily_rate=10.0)
        self.assertEqual(rental.amount_total, 30.0)

    def test_loan_never_carries_the_fee(self):
        """CA4 — un prêt long reste sans frais."""
        loan = self._create_rental("Prêt 10 jours", kind='loan', days=10, daily_rate=10.0)
        self.assertEqual(loan.amount_total, 100.0)

    def test_loan_at_threshold_never_carries_the_fee(self):
        """CA4 — la borne inclusive de cinq jours ne rattrape pas les prêts."""
        loan = self._create_rental("Prêt 5 jours", kind='loan', days=5, daily_rate=10.0)
        self.assertEqual(loan.amount_total, 50.0)

    def test_fee_follows_days_and_kind_changes(self):
        """CA6 — le champ stocké suit les changements de durée et de type."""
        rental = self._create_rental("Location évolutive", days=4, daily_rate=10.0)
        self.assertEqual(rental.amount_total, 40.0)

        rental.days = 5
        self.assertEqual(rental.amount_total, 65.0)

        rental.kind = 'loan'
        self.assertEqual(rental.amount_total, 50.0)

        rental.kind = 'rental'
        self.assertEqual(rental.amount_total, 65.0)

    def test_fee_does_not_depend_on_the_daily_rate(self):
        """CA5 — forfait, donc dû même à tarif nul ; et rien à 0 jour."""
        free_rental = self._create_rental("Location 5 jours gratuite", days=5, daily_rate=0.0)
        self.assertEqual(free_rental.amount_total, PREPARATION_FEE)

        empty_rental = self._create_rental("Location 0 jour", days=0, daily_rate=10.0)
        self.assertEqual(empty_rental.amount_total, 0.0)

    def test_fee_is_flat_not_proportional(self):
        """CA7 — D-03 comme D-02 : le forfait ne varie pas avec le montant loué."""
        cheap = self._create_rental("Location bon marché", days=5, daily_rate=10.0)
        expensive = self._create_rental("Location chère", days=5, daily_rate=1000.0)
        self.assertEqual(cheap.amount_total - 5 * 10.0, PREPARATION_FEE)
        self.assertEqual(expensive.amount_total - 5 * 1000.0, PREPARATION_FEE)

    def test_fee_amount_and_threshold_are_the_ones_of_d03(self):
        """CA12 — verrou sur les deux paramètres que D-03 change.

        Un retour silencieux à 12 EUR ou au seuil de quatre jours doit casser un
        test, pas se glisser dans une reprise."""
        self.assertEqual(PREPARATION_FEE, 15.0)
        self.assertEqual(PREPARATION_FEE_MIN_DAYS, 5)

    def test_stored_value_is_written_in_database(self):
        """CA8 — le total est stocké : la valeur doit être lisible en SQL."""
        rental = self._create_rental("Location stockée", days=6, daily_rate=10.0)
        self.env.flush_all()
        self.env.cr.execute("SELECT amount_total FROM lab_rental WHERE id = %s", [rental.id])
        self.assertEqual(self.env.cr.fetchone()[0], 75.0)
