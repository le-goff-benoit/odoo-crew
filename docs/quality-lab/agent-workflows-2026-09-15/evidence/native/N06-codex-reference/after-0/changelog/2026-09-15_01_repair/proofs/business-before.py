from odoo import fields, models


class LabRegister(models.Model):
    _name = 'lab.register'
    _description = 'Registre synthétique'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    date_document = fields.Date(required=True)
    state = fields.Selection([('draft', 'Draft'), ('issued', 'Issued')], default='draft', required=True)
    sequence = fields.Integer(default=10)
    reference = fields.Char()
    snapshot_total = fields.Float()
    line_ids = fields.One2many('lab.register.line', 'register_id')

    def action_repair(self):
        for index, record in enumerate(self.sudo().search([], order='date_document,id'), 1):
            record.write({'sequence': index * 10, 'snapshot_total': sum(line.quantity * line.price for line in record.line_ids)})
        return True


class LabRegisterLine(models.Model):
    _name = 'lab.register.line'
    _description = 'Ligne de registre synthétique'

    register_id = fields.Many2one('lab.register', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='register_id.company_id', store=True)
    quantity = fields.Float()
    price = fields.Float()
    cancelled = fields.Boolean()
