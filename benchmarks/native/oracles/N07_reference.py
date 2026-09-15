from odoo import api, fields, models


class LabPreparation(models.Model):
    _name = 'lab.preparation'
    _description = 'Préparation synthétique, distincte du stock standard'

    name = fields.Char(required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft', required=True, copy=False)
    ordered_qty = fields.Float()
    delivered_qty = fields.Float(copy=False)
    prepared_qty = fields.Float(copy=False)
    manual = fields.Boolean(copy=False)
    parent_id = fields.Many2one('lab.preparation')

    def action_set_manual(self, quantity):
        self.write({'prepared_qty': quantity, 'manual': True})
        return True

    @api.model
    def _cron_prepare(self):
        for record in self.search([('state', '=', 'draft'), ('manual', '=', False)]):
            record.prepared_qty = max(record.ordered_qty - record.delivered_qty, 0)

    def action_remainder(self):
        self.ensure_one()
        remaining = max(self.ordered_qty - self.delivered_qty, 0)
        if not remaining:
            return self.browse()
        result = self.copy({'name': self.name + ' remainder', 'parent_id': self.id, 'ordered_qty': remaining})
        self.state = 'done'
        return result
