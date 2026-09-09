from odoo import fields, models


class LabDispatch(models.Model):
    _name = 'lab.dispatch'
    _description = 'Dossier logistique synthétique'

    name = fields.Char(required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('done', 'Validé')], default='draft', required=True)
    snapshot_total = fields.Float()
    line_ids = fields.One2many('lab.dispatch.line', 'dispatch_id')

    def action_recalculate(self):
        """Recalculer les brouillons sans toucher aux instantanés validés."""
        for record in self.filtered(lambda record: record.state == 'draft'):
            total = sum(
                line.quantity * line.price
                for line in record.line_ids
                if not line.cancelled
            )
            if record.snapshot_total != total:
                record.snapshot_total = total
        return True


class LabDispatchLine(models.Model):
    _name = 'lab.dispatch.line'
    _description = 'Ligne synthétique'

    dispatch_id = fields.Many2one('lab.dispatch', required=True, ondelete='cascade')
    quantity = fields.Float()
    price = fields.Float()
    cancelled = fields.Boolean()
