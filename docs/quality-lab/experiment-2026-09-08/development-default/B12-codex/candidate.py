# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare


class QualityDelivery(models.Model):
    _name = 'quality_case.delivery'
    _description = 'Synthetic delivery request'

    #=== FIELDS ===#

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company,
    )
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
        """Validate quantities using six decimal places."""
        for delivery in self:
            if float_compare(delivery.ordered_qty, 0.0, precision_digits=6) <= 0:
                raise ValidationError(self.env._(
                    "The ordered quantity must be strictly positive."
                ))
            if float_compare(delivery.available_qty, 0.0, precision_digits=6) < 0:
                raise ValidationError(self.env._(
                    "The available quantity cannot be negative."
                ))

    #=== CRUD ===#

    @api.model_create_multi
    def create(self, vals_list):
        """Initialize protected fields without trusting caller defaults."""
        create_vals_list = []
        for vals in vals_list:
            if vals.get('approved'):
                raise AccessError(self.env._(
                    "Approval can only be granted through the approval action."
                ))
            if vals.get('state', 'draft') != 'draft':
                raise AccessError(self.env._(
                    "A delivery request must be created in draft."
                ))
            if 'create_uid' in vals and vals['create_uid'] != self.env.uid:
                raise AccessError(self.env._(
                    "The creator of a delivery request cannot be changed."
                ))
            create_vals_list.append(dict(
                vals, approved=False, state='draft', create_uid=self.env.uid,
            ))
        deliveries = super().create(create_vals_list)
        # Also validate when quantity fields were omitted from the input.
        deliveries._check_quantities()
        return deliveries

    def write(self, vals):
        """Protect workflow fields and invalidate approval against the last proposal."""
        self.check_access('write')
        if vals.get('approved'):
            raise AccessError(self.env._(
                "Approval can only be granted through the approval action."
            ))
        if 'state' in vals:
            raise AccessError(self.env._(
                "The delivery state can only be changed through the shipping action."
            ))
        # The creator is part of the approval authorization check.
        if 'create_uid' in vals:
            raise AccessError(self.env._(
                "The creator of a delivery request cannot be changed."
            ))
        if (
            vals.get('company_id')
            and not self.env.su
            and vals['company_id'] not in self.env.companies.ids
        ):
            raise AccessError(self.env._(
                "The delivery company must be one of the allowed companies."
            ))

        to_invalidate = self.filtered(lambda delivery: delivery.approved and (
            (
                'available_qty' in vals
                and float_compare(
                    float(vals['available_qty'] or 0.0),
                    delivery.available_qty,
                    precision_digits=6,
                ) < 0
            )
            or (
                'ordered_qty' in vals
                and float_compare(
                    float(vals['ordered_qty'] or 0.0),
                    delivery.ordered_qty,
                    precision_digits=6,
                ) != 0
            )
            or (
                'accepts_partial' in vals
                and bool(vals['accepts_partial']) != delivery.accepts_partial
            )
            or (
                'company_id' in vals
                and vals['company_id'] != delivery.company_id.id
            )
        ))
        if 'approved' in vals:
            vals = dict(vals, approved=False)
        result = super().write(vals)
        if to_invalidate and 'approved' not in vals:
            to_invalidate.write({'approved': False})
        return result

    #=== ACTIONS ===#

    def action_approve(self):
        """Allow an authorized person other than the creator to approve."""
        self.check_access('write')
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError(self.env._(
                "Only an approver can approve a delivery request."
            ))
        if any(delivery.create_uid == self.env.user for delivery in self):
            raise AccessError(self.env._(
                "You cannot approve a delivery request that you created."
            ))
        return super().write({'approved': True})

    def action_ship(self):
        """Ship only when every selected request satisfies the delivery policy."""
        self.check_access('write')
        self._check_quantities()
        for delivery in self:
            if delivery.state != 'draft':
                raise ValidationError(self.env._(
                    "Only draft delivery requests can be shipped."
                ))
            if float_compare(delivery.available_qty, 0.0, precision_digits=6) <= 0:
                raise ValidationError(self.env._(
                    "A delivery cannot be shipped without available quantity."
                ))
            if float_compare(
                delivery.available_qty, delivery.ordered_qty, precision_digits=6,
            ) >= 0:
                continue
            if not delivery.accepts_partial:
                raise ValidationError(self.env._(
                    "The full ordered quantity must be available before shipping."
                ))
            if (
                float_compare(
                    delivery.available_qty,
                    delivery.ordered_qty * 0.6,
                    precision_digits=6,
                ) < 0
                and not delivery.approved
            ):
                raise ValidationError(self.env._(
                    "Approval is required to ship less than 60% of the ordered quantity."
                ))
        return super().write({'state': 'done'})
