from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPreparationFee(TransactionCase):
    """Decision D-03 (decisions/2026-09-09.md): flat 15 EUR preparation fee on
    rentals of five days or more, loans excluded. Expected amounts come from the
    decision itself, never from the method under test.

    D-03 supersedes D-02 (12 EUR from four days) and D-01 (7% of the price).
    Both superseded rules are covered by explicit regression tests below.
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

    #=== The five-day bound is inclusive ===#

    def test_rental_below_threshold_has_no_fee(self):
        """Three days: under the bound, the total is the bare rental price."""
        self.assertEqual(self._rental(3, 10.0).amount_total, 30.0)

    def test_rental_just_below_threshold_has_no_fee(self):
        """Four days: D-02 charged this rental, D-03 does not any more."""
        self.assertEqual(self._rental(4, 10.0).amount_total, 40.0)

    def test_rental_at_threshold_bears_the_fee(self):
        """Five days: the bound is inclusive, so the fee is due."""
        self.assertEqual(self._rental(5, 10.0).amount_total, 65.0)

    def test_rental_above_threshold_bears_the_fee_once(self):
        """Seven days: the fee is flat, it is not charged per day."""
        self.assertEqual(self._rental(7, 20.0).amount_total, 155.0)

    #=== Loans are excluded ===#

    def test_loan_at_threshold_has_no_fee(self):
        """A five-day loan stays free of charge, unlike a five-day rental."""
        self.assertEqual(self._rental(5, 10.0, kind='loan').amount_total, 50.0)

    def test_long_loan_has_no_fee(self):
        """No duration ever makes a loan bear the preparation fee."""
        self.assertEqual(self._rental(10, 10.0, kind='loan').amount_total, 100.0)

    #=== Boundary values of the domain ===#

    def test_empty_rental_is_free(self):
        """Zero day and zero rate: nothing is due, not even the fee."""
        self.assertEqual(self._rental(0, 0.0).amount_total, 0.0)

    def test_fee_does_not_depend_on_the_daily_rate(self):
        """D-03 conditions the fee on kind and duration only, not on the price."""
        self.assertEqual(self._rental(5, 0.0).amount_total, 15.0)

    #=== The stored field follows the record ===#

    def test_crossing_the_threshold_updates_the_stored_total(self):
        """Going from four to five days adds the fee to the stored total."""
        rental = self._rental(4, 10.0)
        self.assertEqual(rental.amount_total, 40.0)
        rental.days = 5
        self.assertEqual(rental.amount_total, 65.0)

    def test_turning_a_rental_into_a_loan_removes_the_fee(self):
        """The recomputation is symmetric: the fee disappears with the kind."""
        rental = self._rental(6, 10.0)
        self.assertEqual(rental.amount_total, 75.0)
        rental.kind = 'loan'
        self.assertEqual(rental.amount_total, 60.0)

    #=== Superseded decisions must not come back ===#

    def test_the_fee_is_flat_and_never_proportional(self):
        """Two rentals of the same duration bear the very same fee, 15 EUR.

        Under superseded decision D-01 the fee was 7% of the price, so it grew
        with the daily rate. This test fails if that rule ever comes back, and
        also if the D-02 amount of 12 EUR is restored.
        """
        cheap = self._rental(6, 10.0)
        expensive = self._rental(6, 1000.0)
        self.assertEqual(cheap.amount_total - 6 * 10.0, 15.0)
        self.assertEqual(expensive.amount_total - 6 * 1000.0, 15.0)

    def test_the_four_day_rental_no_longer_bears_the_superseded_fee(self):
        """D-02 charged 12 EUR from four days; D-03 moved the bound to five.

        Kept as an explicit regression test because D-02 was implemented and
        validated in this very release before being superseded: the repository
        history, the journal and the previous proofs all still show 52.0 here.
        """
        self.assertEqual(self._rental(4, 10.0).amount_total, 40.0)
        self.assertEqual(self._rental(4, 1000.0).amount_total, 4000.0)
