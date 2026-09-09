from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPreparationFee(TransactionCase):
    """Decision D-02 (decisions/2026-09-08.md): flat 12 EUR preparation fee on
    rentals of four days or more, loans excluded. Expected amounts come from the
    decision itself, never from the method under test.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Rental = cls.env['lab.rental']

    def _rental(self, days, daily_rate, kind='rental'):
        return self.Rental.create({
            'name': f'{kind} {days}d',
            'days': days,
            'daily_rate': daily_rate,
            'kind': kind,
        })

    #=== Q1 — the four-day bound is inclusive ===#

    def test_rental_below_threshold_has_no_fee(self):
        """Three days: under the bound, the total is the bare rental price."""
        self.assertEqual(self._rental(3, 10.0).amount_total, 30.0)

    def test_rental_at_threshold_bears_the_fee(self):
        """Four days: the bound is inclusive, so the fee is due."""
        self.assertEqual(self._rental(4, 10.0).amount_total, 52.0)

    def test_rental_above_threshold_bears_the_fee_once(self):
        """Seven days: the fee is flat, it is not charged per day."""
        self.assertEqual(self._rental(7, 10.0).amount_total, 82.0)

    #=== Q2 — loans are excluded ===#

    def test_loan_at_threshold_has_no_fee(self):
        """A four-day loan stays free of charge, unlike a four-day rental."""
        self.assertEqual(self._rental(4, 10.0, kind='loan').amount_total, 40.0)

    def test_long_loan_has_no_fee(self):
        """No duration ever makes a loan bear the preparation fee."""
        self.assertEqual(self._rental(10, 10.0, kind='loan').amount_total, 100.0)

    #=== Boundary values of the domain ===#

    def test_empty_rental_is_free(self):
        """Zero day and zero rate: nothing is due, not even the fee."""
        self.assertEqual(self._rental(0, 0.0).amount_total, 0.0)

    def test_fee_does_not_depend_on_the_daily_rate(self):
        """D-02 conditions the fee on kind and duration only, not on the price."""
        self.assertEqual(self._rental(5, 0.0).amount_total, 12.0)

    #=== The stored field follows the record ===#

    def test_crossing_the_threshold_updates_the_stored_total(self):
        """Going from three to four days adds the fee to the stored total."""
        rental = self._rental(3, 10.0)
        self.assertEqual(rental.amount_total, 30.0)
        rental.days = 4
        self.assertEqual(rental.amount_total, 52.0)

    def test_turning_a_rental_into_a_loan_removes_the_fee(self):
        """The recomputation is symmetric: the fee disappears with the kind."""
        rental = self._rental(5, 10.0)
        self.assertEqual(rental.amount_total, 62.0)
        rental.kind = 'loan'
        self.assertEqual(rental.amount_total, 50.0)

    #=== D-01 (7% proportional fee) is superseded and must not come back ===#

    def test_the_fee_is_flat_and_never_proportional(self):
        """Two rentals of the same duration bear the very same fee, 12 EUR.

        Under superseded decision D-01 the fee was 7% of the price, so it grew
        with the daily rate. This test fails if that rule ever comes back.
        """
        cheap = self._rental(6, 10.0)
        expensive = self._rental(6, 1000.0)
        self.assertEqual(cheap.amount_total - 6 * 10.0, 12.0)
        self.assertEqual(expensive.amount_total - 6 * 1000.0, 12.0)
