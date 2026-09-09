from odoo import api, fields, models


class LabRental(models.Model):
    _name = 'lab.rental'
    _description = 'Location synthétique'

    _days_nonnegative = models.Constraint(
        'CHECK(days >= 0)',
        'Le nombre de jours doit être positif ou nul.',
    )
    _daily_rate_nonnegative = models.Constraint(
        'CHECK(daily_rate >= 0)',
        'Le tarif journalier doit être positif ou nul.',
    )

    name = fields.Char(required=True)
    days = fields.Integer(default=0)
    daily_rate = fields.Float(default=0)
    kind = fields.Selection([('rental', 'Location'), ('loan', 'Prêt')], default='rental', required=True)
    amount_total = fields.Float(compute='_compute_amount_total', store=True)

    @api.depends('days', 'daily_rate', 'kind')
    def _compute_amount_total(self):
        """Appliquer le forfait de préparation D-02 aux locations éligibles."""
        for record in self:
            record.amount_total = record.days * record.daily_rate
            if record.kind == 'rental' and record.days >= 4:
                record.amount_total += 12
