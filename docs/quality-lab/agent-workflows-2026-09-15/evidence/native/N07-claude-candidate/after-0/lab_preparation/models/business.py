from odoo import api, fields, models


class LabPreparation(models.Model):
    _name = 'lab.preparation'
    _description = 'Préparation synthétique, distincte du stock standard'

    name = fields.Char(required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done')], default='draft', required=True, copy=False)
    ordered_qty = fields.Float()
    delivered_qty = fields.Float(copy=False)
    prepared_qty = fields.Float(copy=False)
    manual = fields.Boolean(copy=False)
    parent_id = fields.Many2one('lab.preparation')

    #=== BUSINESS METHODS ===#

    def action_set_manual(self, quantity):
        """Record an explicit prepared quantity, shielded from the cron.

        Zero is a valid decision, not an empty value: the record is flagged as
        manual whatever the quantity, otherwise the next automatic pass would
        silently overwrite it.
        """
        self.write({'prepared_qty': quantity, 'manual': True})
        return True

    @api.model
    def _cron_prepare(self):
        """Compute what is left to prepare on automatic drafts.

        Manual entries and done preparations are out of reach: only drafts the
        user never touched are recomputed, which makes the pass idempotent.
        """
        automatic_drafts = self.search([('state', '=', 'draft'), ('manual', '=', False)])
        for preparation in automatic_drafts:
            preparation.prepared_qty = preparation._get_remainder_qty()

    def action_remainder(self):
        """Split off what is left to deliver into a new draft.

        Returns the new preparation, or an empty recordset when there is
        nothing left — in that case the source is left untouched.
        """
        self.ensure_one()
        remainder_qty = self._get_remainder_qty()
        if remainder_qty <= 0:
            return self.browse()
        remainder = self.copy({
            'name': self.name + ' remainder',
            'ordered_qty': remainder_qty,
            'parent_id': self.id,
        })
        # Closing the source must not touch its prepared quantity, which may
        # hold a manual entry.
        self.state = 'done'
        return remainder

    def _get_remainder_qty(self):
        """Return what is left to prepare, never a negative quantity."""
        self.ensure_one()
        return max(self.ordered_qty - self.delivered_qty, 0)
