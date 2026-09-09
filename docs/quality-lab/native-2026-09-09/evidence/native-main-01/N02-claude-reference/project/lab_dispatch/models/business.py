from odoo import fields, models


class LabDispatch(models.Model):
    _name = 'lab.dispatch'
    _description = 'Dossier logistique synthétique'

    name = fields.Char(required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('done', 'Validé')], default='draft', required=True)
    snapshot_total = fields.Float()
    line_ids = fields.One2many('lab.dispatch.line', 'dispatch_id')

    #=== ACTIONS ===#

    def action_recalculate(self):
        """Recalcule le total des dossiers en brouillon, hors lignes annulées.

        Un dossier validé porte un total figé (D-12) : il est écarté avant toute
        écriture, et non pas recalculé puis comparé — réécrire la même valeur reste
        une écriture. Une sélection mixte recalcule les brouillons sans lever d'erreur.
        """
        for record in self.filtered(lambda record: record.state == 'draft'):
            record.snapshot_total = sum(
                line.quantity * line.price
                for line in record.line_ids
                if not line.cancelled
            )
        return True


class LabDispatchLine(models.Model):
    _name = 'lab.dispatch.line'
    _description = 'Ligne synthétique'

    dispatch_id = fields.Many2one('lab.dispatch', required=True, ondelete='cascade')
    quantity = fields.Float()
    price = fields.Float()
    cancelled = fields.Boolean()
