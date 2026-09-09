from odoo import api, fields, models


class LabRental(models.Model):
    _name = 'lab.rental'
    _description = 'Location synthétique'

    #=== CONSTANTS ===#

    PREPARATION_FEE = 15.0
    PREPARATION_FEE_MIN_DAYS = 5

    #=== FIELDS ===#

    name = fields.Char(required=True)
    days = fields.Integer(default=0)
    daily_rate = fields.Float(default=0)
    kind = fields.Selection([('rental', 'Location'), ('loan', 'Prêt')], default='rental', required=True)
    amount_total = fields.Float(compute='_compute_amount_total', store=True)

    #=== COMPUTE METHODS ===#

    @api.depends('days', 'daily_rate', 'kind')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.days * record.daily_rate + record._preparation_fee()

    #=== BUSINESS METHODS ===#

    def _preparation_fee(self):
        """Return the flat preparation fee due for this rental.

        Decision D-03 (2026-09-09): a fixed 15 EUR fee applies to rentals of five
        days or more, the bound being inclusive. Loans never bear the fee, whatever
        their duration. The fee is flat, never proportional.

        D-03 supersedes D-02 (12 EUR from four days), which itself superseded D-01
        (7% of the price). A four-day rental therefore bears no fee at all any more:
        its stored total goes down. Both superseded rules are pinned by regression
        tests so that neither can come back unnoticed.
        """
        self.ensure_one()
        is_long_enough = self.days >= self.PREPARATION_FEE_MIN_DAYS
        return self.PREPARATION_FEE if self.kind == 'rental' and is_long_enough else 0.0
