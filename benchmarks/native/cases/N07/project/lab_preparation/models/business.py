from odoo import api, fields, models


class LabPreparation(models.Model):
    _name = 'lab.preparation'
    _description = 'Préparation synthétique, distincte du stock standard'

    name = fields.Char(required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft', required=True)
    ordered_qty = fields.Float()
    delivered_qty = fields.Float()
    prepared_qty = fields.Float()
    manual = fields.Boolean()
    parent_id = fields.Many2one('lab.preparation')

    def action_set_manual(self, quantity):
        self.write({'prepared_qty': quantity, 'manual': bool(quantity)})
        return True

    @api.model
    def _cron_prepare(self):
        for record in self.search([]):
            record.prepared_qty = record.ordered_qty

    def action_remainder(self):
        self.ensure_one()
        return self.copy({'name': self.name + ' remainder', 'parent_id': self.id})
