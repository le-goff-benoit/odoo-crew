# Part of Odoo. See LICENSE file for full copyright and licensing details.

import math

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
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done')],
        default='draft', required=True, readonly=True, copy=False,
    )

    #=== CONSTRAINTS ===#

    @api.constrains('ordered_qty', 'available_qty')
    def _check_quantities(self):
        """Keep quantities finite and valid at the business precision."""
        for delivery in self:
            if not math.isfinite(delivery.ordered_qty) or float_compare(
                delivery.ordered_qty, 0.0, precision_digits=6,
            ) <= 0:
                raise ValidationError(self.env._('The ordered quantity must be strictly positive.'))
            if not math.isfinite(delivery.available_qty) or float_compare(
                delivery.available_qty, 0.0, precision_digits=6,
            ) < 0:
                raise ValidationError(self.env._('The available quantity cannot be negative.'))

    #=== CRUD ===#

    @api.model_create_multi
    def create(self, vals_list):
        """Initialize protected fields explicitly, including against context defaults."""
        self.check_access('create')
        defaults = self.default_get(['company_id'])
        allowed_company_ids = self.env.companies.ids
        create_vals_list = []
        for vals in vals_list:
            if vals.get('approved') or vals.get('state', 'draft') != 'draft':
                raise AccessError(self.env._('Approval and shipment require their dedicated actions.'))
            if 'create_uid' in vals:
                raise AccessError(self.env._('The creator cannot be supplied manually.'))
            company_id = vals.get('company_id', defaults.get('company_id'))
            if company_id not in allowed_company_ids:
                raise AccessError(self.env._('The company must be one of your active companies.'))
            create_vals_list.append(dict(
                vals,
                company_id=company_id,
                approved=False,
                state='draft',
                create_uid=self.env.uid,
            ))
        return super().create(create_vals_list)

    def write(self, vals):
        """Invalidate approval against the immediately preceding proposal."""
        self.check_access('read')
        self.check_access('write')
        if {'approved', 'state', 'create_uid'} & vals.keys():
            raise AccessError(self.env._('Protected fields cannot be changed manually.'))
        if 'company_id' in vals and vals['company_id'] not in self.env.companies.ids:
            raise AccessError(self.env._('The company must be one of your active companies.'))

        to_invalidate = self.filtered(lambda delivery: delivery.approved and (
            ('available_qty' in vals and float_compare(
                vals['available_qty'], delivery.available_qty, precision_digits=6,
            ) < 0)
            or ('ordered_qty' in vals and float_compare(
                vals['ordered_qty'], delivery.ordered_qty, precision_digits=6,
            ) != 0)
            or ('accepts_partial' in vals
                and bool(vals['accepts_partial']) != delivery.accepts_partial)
            or ('company_id' in vals and vals['company_id'] != delivery.company_id.id)
        ))
        if to_invalidate:
            super(QualityDelivery, to_invalidate).write(dict(vals, approved=False))
        remaining = self - to_invalidate
        if remaining:
            super(QualityDelivery, remaining).write(vals)
        return True

    #=== ACTIONS ===#

    def action_approve(self):
        """Approve only after checking company access, membership and separation of duties."""
        self.check_access('read')
        self.check_access('write')
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError(self.env._('Only approvers can approve a delivery request.'))
        if any(delivery.create_uid == self.env.user for delivery in self):
            raise AccessError(self.env._('You cannot approve your own delivery request.'))
        # Bypass the public field guard only after validating the actual caller.
        return super().write({'approved': True})

    def action_ship(self):
        """Validate every request before performing the protected shipment transition."""
        self.check_access('read')
        self.check_access('write')
        for delivery in self:
            if delivery.state != 'draft':
                raise ValidationError(self.env._('Only draft delivery requests can be shipped.'))
            if float_compare(delivery.available_qty, 0.0, precision_digits=6) <= 0:
                raise ValidationError(self.env._('A delivery cannot be shipped without available quantity.'))
            if float_compare(
                delivery.available_qty, delivery.ordered_qty, precision_digits=6,
            ) >= 0:
                continue
            if not delivery.accepts_partial:
                raise ValidationError(self.env._('The full ordered quantity must be available.'))
            if float_compare(
                delivery.available_qty, delivery.ordered_qty * 0.6, precision_digits=6,
            ) < 0 and not delivery.approved:
                raise ValidationError(self.env._('Shipping less than 60%% requires approval.'))
        # All records must pass access and business checks before changing state.
        return super().write({'state': 'done'})
