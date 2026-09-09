from odoo import api, fields, models

# Frais de préparation — décision D-03 du 09/09/2026 (decisions/2026-09-09.md).
# Forfait fixe, hors taxes, en EUR, et non proportionnel à la durée : la remise en
# état d'un bien coûte le même temps qu'on le loue cinq jours ou trois semaines.
# D-03 remplace D-02 (12 EUR dès quatre jours), qui remplaçait D-01 (7 % du total).
# Historique utile au relecteur : ni le forfait de 12 EUR, ni le seuil de quatre
# jours, ni aucun frais proportionnel n'a plus cours dans ce module.
PREPARATION_FEE = 15.0
PREPARATION_FEE_MIN_DAYS = 5


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
        for record in self:
            record.amount_total = record.days * record.daily_rate + record._preparation_fee()

    def _preparation_fee(self):
        """Return the flat preparation fee due for this rental, 0 if none.

        Rentals of five days or more carry the fee — the bound is inclusive (D-03).
        Loans never carry it, whatever their duration.
        """
        self.ensure_one()
        if self.kind == 'rental' and self.days >= PREPARATION_FEE_MIN_DAYS:
            return PREPARATION_FEE
        return 0.0
