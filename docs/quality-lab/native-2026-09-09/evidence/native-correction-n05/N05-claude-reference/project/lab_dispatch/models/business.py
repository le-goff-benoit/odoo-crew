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
        """Recalcule le total des seuls dossiers brouillons (D-12).

        Un dossier validé est un instantané figé : il est ignoré sans erreur et
        sans écriture, y compris quand la sélection en contient. Les lignes
        annulées sont exclues du total.
        """
        for record in self.filtered(lambda dispatch: dispatch.state == 'draft'):
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
