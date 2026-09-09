from odoo import api, fields, models


class LabRental(models.Model):
    _name = 'lab.rental'
    _description = 'Location synthétique'

    name = fields.Char(required=True)
    days = fields.Integer(default=0)
    daily_rate = fields.Float(default=0)
    kind = fields.Selection([('rental', 'Location'), ('loan', 'Prêt')], default='rental', required=True)
    amount_total = fields.Float(compute='_compute_amount_total', store=True)

    @api.depends('days', 'daily_rate', 'kind')
    def _compute_amount_total(self):
        """Inclure le forfait de préparation D-03 des locations éligibles."""
        for record in self:
            record.amount_total = record.days * record.daily_rate
            if record.kind == 'rental' and record.days >= 5:
                record.amount_total += 15
