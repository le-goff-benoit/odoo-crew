# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare


class QualityDelivery(models.Model):
    _name = 'quality_case.delivery'
    _description = 'Synthetic delivery request'

    #=== PRIVATE ATTRIBUTES ===#

    # Quantities are compared at six decimals, as agreed in the S-01 contract.
    _qty_precision = 6
    # Minimum shipped ratio allowed without an approver agreement.
    _partial_ratio = 0.6
    # Context key used internally to write protected fields (approved, state).
    _protected_context_key = 'quality_case_protected_write'

    #=== FIELDS ===#

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    ordered_qty = fields.Float(required=True)
    available_qty = fields.Float(required=True)
    accepts_partial = fields.Boolean()
    approved = fields.Boolean(readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft', required=True, readonly=True)

    #=== CONSTRAINT METHODS ===#

    @api.constrains('ordered_qty', 'available_qty')
    def _check_quantities(self):
        """Ordered quantity is strictly positive, available quantity is never negative."""
        for delivery in self:
            if float_compare(delivery.ordered_qty, 0.0, precision_digits=self._qty_precision) <= 0:
                raise ValidationError(self.env._("The ordered quantity must be strictly positive."))
            if float_compare(delivery.available_qty, 0.0, precision_digits=self._qty_precision) < 0:
                raise ValidationError(self.env._("The available quantity cannot be negative."))

    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        """Prevent forging the approval or the final state at creation time."""
        if not self.env.context.get(self._protected_context_key):
            vals_list = [self._filter_protected_vals(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        """Protect the approval fields and invalidate a stale agreement.

        The agreement only survives a proposal that goes up: any decrease of the
        available quantity compared to the immediately preceding proposal, and any
        change of the order itself, cancels it.
        """
        if self.env.context.get(self._protected_context_key):
            return super().write(vals)

        vals = self._filter_protected_vals(vals)
        to_unapprove = self.browse()
        for delivery in self:
            if delivery.approved and delivery._is_approval_invalidated(vals):
                to_unapprove |= delivery

        res = super().write(vals)
        if to_unapprove:
            super(QualityDelivery, to_unapprove).write({'approved': False})
        return res

    #=== ACTION METHODS ===#

    def action_approve(self):
        """Record the manager agreement allowing a partial shipment."""
        self.check_access('write')
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError(self.env._("Only an approver can approve a delivery request."))
        for delivery in self:
            if delivery.create_uid == self.env.user:
                raise AccessError(self.env._("A delivery request must be approved by another user."))
        self.with_context(**{self._protected_context_key: True}).write({'approved': True})
        return True

    def action_ship(self):
        """Ship the request when the available quantity allows it."""
        self.check_access('write')
        for delivery in self:
            delivery._check_shippable()
        self.with_context(**{self._protected_context_key: True}).write({'state': 'done'})
        return True

    #=== BUSINESS METHODS ===#

    def _filter_protected_vals(self, vals):
        """Return ``vals`` without the fields only the workflow may set."""
        return {key: value for key, value in vals.items() if key not in ('approved', 'state')}

    def _is_approval_invalidated(self, vals):
        """Return whether the values about to be written cancel the agreement."""
        self.ensure_one()
        if 'ordered_qty' in vals and float_compare(
            vals['ordered_qty'] or 0.0, self.ordered_qty, precision_digits=self._qty_precision
        ) != 0:
            return True
        if 'accepts_partial' in vals and bool(vals['accepts_partial']) != self.accepts_partial:
            return True
        if 'company_id' in vals and (vals['company_id'] or False) != (self.company_id.id or False):
            return True
        if 'available_qty' in vals and float_compare(
            vals['available_qty'] or 0.0, self.available_qty, precision_digits=self._qty_precision
        ) < 0:
            return True
        return False

    def _check_shippable(self):
        """Raise if the request cannot be shipped as it stands."""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(self.env._("Only a draft delivery request can be shipped."))
        if float_compare(self.available_qty, 0.0, precision_digits=self._qty_precision) <= 0:
            raise ValidationError(self.env._("Nothing is available for this delivery request."))
        if float_compare(self.available_qty, self.ordered_qty, precision_digits=self._qty_precision) >= 0:
            return
        if not self.accepts_partial:
            raise ValidationError(self.env._("This delivery request does not accept a partial shipment."))
        threshold = self.ordered_qty * self._partial_ratio
        if float_compare(self.available_qty, threshold, precision_digits=self._qty_precision) >= 0:
            return
        if not self.approved:
            raise ValidationError(self.env._(
                "A manager approval is required to ship less than %(ratio)s%% of the ordered quantity.",
                ratio=int(self._partial_ratio * 100),
            ))
