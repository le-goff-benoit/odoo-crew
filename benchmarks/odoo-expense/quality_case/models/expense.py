from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare


class QualityExpense(models.Model):
    _name = 'quality_case.expense'
    _description = 'Synthetic expense request'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    amount = fields.Float(required=True)
    approved = fields.Boolean(readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], default='draft', required=True, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        defaults = self.default_get(['approved', 'state'])
        if any(v.get('approved', defaults.get('approved')) or v.get('state', defaults.get('state', 'draft')) != 'draft' for v in vals_list):
            raise AccessError('Dedicated actions required.')
        return super().create(vals_list)

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if float_compare(record.amount, 0, precision_digits=2) <= 0:
                raise ValidationError('A positive amount is required.')

    def write(self, vals):
        if {'approved', 'state'} & vals.keys():
            raise AccessError('Dedicated actions required.')
        invalidated = self.filtered(lambda r: ('amount' in vals and float_compare(vals['amount'], r.amount, precision_digits=2) > 0)
                                    or ('company_id' in vals and vals['company_id'] != r.company_id.id))
        result = super().write(vals)
        if invalidated:
            super(QualityExpense, invalidated).write({'approved': False})
        return result

    def action_approve(self):
        self.check_access('write')
        if not self.env.user.has_group('quality_case.group_approver') or any(r.create_uid == self.env.user for r in self):
            raise AccessError('An independent approver is required.')
        super().write({'approved': True})
        return True

    def action_pay(self):
        self.check_access('write')
        for record in self:
            if float_compare(record.amount, 250, precision_digits=2) > 0 and not record.approved:
                raise ValidationError('Approval required above 250.')
        super().write({'state': 'paid'})
        return True
