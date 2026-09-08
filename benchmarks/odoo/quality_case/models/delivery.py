from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare


class QualityDelivery(models.Model):
    _name = 'quality_case.delivery'
    _description = 'Synthetic delivery request'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    ordered_qty = fields.Float(required=True)
    available_qty = fields.Float(required=True)
    accepts_partial = fields.Boolean()
    approved = fields.Boolean(readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft', required=True, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        defaults = self.default_get(['approved', 'state'])
        if any(vals.get('approved', defaults.get('approved')) or
               vals.get('state', defaults.get('state', 'draft')) != 'draft' for vals in vals_list):
            raise AccessError('Approval and shipping require their dedicated actions.')
        return super().create(vals_list)

    @api.constrains('ordered_qty', 'available_qty')
    def _check_quantities(self):
        for record in self:
            if record.ordered_qty <= 0 or record.available_qty < 0:
                raise ValidationError('Ordered quantity must be positive; availability cannot be negative.')

    def write(self, vals):
        if {'approved', 'state'} & vals.keys():
            raise AccessError('Approval and shipping require their dedicated actions.')
        # S-01: compare to the immediately preceding proposal, not a historic maximum.
        invalidate = self.filtered(lambda r: (
            'available_qty' in vals and float_compare(vals['available_qty'], r.available_qty, precision_digits=6) < 0
        ) or ('ordered_qty' in vals and float_compare(vals['ordered_qty'], r.ordered_qty, precision_digits=6) != 0)
          or ('accepts_partial' in vals and bool(vals['accepts_partial']) != r.accepts_partial)
          or ('company_id' in vals and vals['company_id'] != r.company_id.id))
        result = super().write(vals)
        if invalidate:
            super(QualityDelivery, invalidate).write({'approved': False})
        return result

    def action_approve(self):
        self.check_access('write')
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError('Approver role required.')
        if any(record.create_uid == self.env.user for record in self):
            raise AccessError('A requester cannot approve their own request.')
        super().write({'approved': True})
        return True

    def action_ship(self):
        self.check_access('write')
        for record in self:
            full = float_compare(record.available_qty, record.ordered_qty, precision_digits=6) >= 0
            threshold = float_compare(record.available_qty, record.ordered_qty * 0.6, precision_digits=6) >= 0
            if record.available_qty <= 0 or (not full and (
                not record.accepts_partial or (not threshold and not record.approved)
            )):
                raise ValidationError('Delivery is not authorized by the current business rule.')
        super().write({'state': 'done'})
        return True
