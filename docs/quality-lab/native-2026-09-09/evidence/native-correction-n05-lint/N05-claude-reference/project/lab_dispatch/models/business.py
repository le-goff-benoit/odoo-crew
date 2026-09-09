from odoo import fields, models


class LabDispatch(models.Model):
    _name = 'lab.dispatch'
    _description = 'Dossier logistique synthétique'

    name = fields.Char(required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('done', 'Validé')], default='draft', required=True)
    snapshot_total = fields.Float()
    line_ids = fields.One2many('lab.dispatch.line', 'dispatch_id')

    def action_recalculate(self):
        """Recalculer le total figé des seuls dossiers en brouillon.

        Le total d'un dossier validé est définitivement figé : il n'est ni
        réécrit ni recalculé, même lorsqu'il fait partie d'une sélection mixte.
        """
        for record in self.filtered(lambda dispatch: dispatch.state == 'draft'):
            record.snapshot_total = record._get_lines_total()
        return True

    def _get_lines_total(self):
        """Renvoyer la somme des lignes non annulées du dossier."""
        self.ensure_one()
        return sum(line.quantity * line.price for line in self.line_ids if not line.cancelled)


class LabDispatchLine(models.Model):
    _name = 'lab.dispatch.line'
    _description = 'Ligne synthétique'

    dispatch_id = fields.Many2one('lab.dispatch', required=True, ondelete='cascade')
    quantity = fields.Float()
    price = fields.Float()
    cancelled = fields.Boolean()
