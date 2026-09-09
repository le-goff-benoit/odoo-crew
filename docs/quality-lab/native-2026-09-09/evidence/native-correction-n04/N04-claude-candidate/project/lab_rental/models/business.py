from odoo import api, fields, models


class LabRental(models.Model):
    _name = 'lab.rental'
    _description = 'Location synthétique'

    name = fields.Char(required=True)
    days = fields.Integer(default=0)
    daily_rate = fields.Float(default=0)
    kind = fields.Selection([('rental', 'Location'), ('loan', 'Prêt')], default='rental', required=True)
    amount_total = fields.Float(compute='_compute_amount_total', store=True)

    _days_positive = models.Constraint(
        'CHECK (days >= 0)',
        "La durée d'une location ne peut pas être négative (zéro est permis).",
    )

    @api.depends('days', 'daily_rate', 'kind')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.days * record.daily_rate
