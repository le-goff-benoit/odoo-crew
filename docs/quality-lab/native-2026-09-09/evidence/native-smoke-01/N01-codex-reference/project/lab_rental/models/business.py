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
        """Inclure le forfait D-02 pour les locations d'au moins quatre jours."""
        for record in self:
            preparation_fee = 12 if record.kind == 'rental' and record.days >= 4 else 0
            record.amount_total = record.days * record.daily_rate + preparation_fee
