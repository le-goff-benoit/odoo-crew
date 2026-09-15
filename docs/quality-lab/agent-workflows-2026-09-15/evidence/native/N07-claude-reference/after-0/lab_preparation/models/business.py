from odoo import api, fields, models


class LabPreparation(models.Model):
    _name = 'lab.preparation'
    _description = 'Préparation synthétique, distincte du stock standard'

    name = fields.Char(required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done')],
        default='draft', required=True, copy=False,
    )
    ordered_qty = fields.Float()
    # Une duplication est une nouvelle demande : elle ne reprend que la quantité
    # commandée, jamais l'historique de préparation de la source (décision N-17).
    delivered_qty = fields.Float(copy=False)
    prepared_qty = fields.Float(copy=False)
    manual = fields.Boolean(copy=False)
    parent_id = fields.Many2one('lab.preparation')

    #=== ACTION METHODS ===#

    def action_set_manual(self, quantity):
        """Enregistre une quantité saisie à la main ; zéro est une valeur valide."""
        self.write({'prepared_qty': quantity, 'manual': True})
        return True

    def action_remainder(self):
        """Clôt la préparation et ouvre le reliquat du reste à préparer.

        Retourne un recordset vide quand il n'y a pas de reste positif : la
        source est close, mais aucune ligne n'est créée.
        """
        self.ensure_one()
        remaining = self.ordered_qty - self.delivered_qty
        remainder = self.browse()
        if remaining > 0:
            remainder = self.create({
                'name': self.name + ' remainder',
                'ordered_qty': remaining,
                'delivered_qty': 0.0,
                'prepared_qty': 0.0,
                'manual': False,
                'state': 'draft',
                'parent_id': self.id,
            })
        # La quantité déjà préparée sur la source reste son résultat propre.
        self.state = 'done'
        return remainder

    #=== BUSINESS METHODS ===#

    @api.model
    def _cron_prepare(self):
        """Recalcule les seules préparations automatiques encore en brouillon."""
        for record in self.search([('state', '=', 'draft'), ('manual', '=', False)]):
            record.prepared_qty = max(record.ordered_qty - record.delivered_qty, 0.0)
