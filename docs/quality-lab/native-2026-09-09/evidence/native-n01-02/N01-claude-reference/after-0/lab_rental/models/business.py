from odoo import api, fields, models

# === CONSTANTES MÉTIER (D-02, decisions/2026-09-08.md) === #

# Forfait de préparation, hors taxes, en EUR : montant fixe par location, pas par jour.
PREPARATION_FEE = 12.0
# Durée à partir de laquelle le forfait s'applique. Borne inclusive (Q1) : 4 jours comptent.
PREPARATION_FEE_MIN_DAYS = 4


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
        """Forfait de préparation dû par cet engagement, selon D-02.

        Les prêts en sont exclus quelle que soit leur durée (Q2) ; les locations le
        doivent à partir de PREPARATION_FEE_MIN_DAYS jours, borne comprise (Q1).
        Méthode séparée pour que la règle reste lisible et surchargeable.
        """
        self.ensure_one()
        if self.kind == 'rental' and self.days >= PREPARATION_FEE_MIN_DAYS:
            return PREPARATION_FEE
        return 0.0
