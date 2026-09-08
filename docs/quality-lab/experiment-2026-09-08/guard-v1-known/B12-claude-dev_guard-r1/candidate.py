# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare


class QualityDelivery(models.Model):
    _name = 'quality_case.delivery'
    _description = 'Synthetic delivery request'

    # Quantities are compared with six decimals, as agreed in the S-01 contract.
    QTY_DIGITS = 6
    # Minimum shipped ratio (included) allowed without a manager approval.
    PARTIAL_RATIO = 0.6
    # Fields whose modification invalidates a previously granted approval.
    APPROVAL_RESET_FIELDS = ('ordered_qty', 'accepts_partial', 'company_id')
    # Fields that may only be set by the dedicated actions, never through create/write.
    PROTECTED_FIELDS = ('approved', 'state')

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
            if float_compare(delivery.ordered_qty, 0.0, precision_digits=self.QTY_DIGITS) <= 0:
                raise ValidationError(self.env._("The ordered quantity must be strictly positive."))
            if float_compare(delivery.available_qty, 0.0, precision_digits=self.QTY_DIGITS) < 0:
                raise ValidationError(self.env._("The available quantity cannot be negative."))

    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        """Never let an approval or a final state be forged at creation time.

        The protected values are dropped instead of raising, so that a caller
        passing them (directly or through a ``default_*`` context key) still
        gets a record left in its safe state.
        """
        vals_list = [
            {key: value for key, value in vals.items() if key not in self.PROTECTED_FIELDS}
            for vals in vals_list
        ]
        return super().create(vals_list)

    def write(self, vals):
        """Drop the protected values and invalidate the approval when needed.

        The approval is lost when the proposal goes down compared to the
        *immediately previous* one, or when one of the fields it was granted
        for is actually modified. Going up keeps it.
        """
        vals = {key: value for key, value in vals.items() if key not in self.PROTECTED_FIELDS}
        if not vals:
            return True

        to_reset = self.browse()
        for delivery in self:
            if not delivery.approved:
                continue
            if 'available_qty' in vals and float_compare(
                vals['available_qty'], delivery.available_qty, precision_digits=self.QTY_DIGITS
            ) < 0:
                to_reset |= delivery
            elif delivery._approval_fields_changed(vals):
                to_reset |= delivery

        res = super().write(vals)
        if to_reset:
            super(QualityDelivery, to_reset).write({'approved': False})
        return res

    def _approval_fields_changed(self, vals):
        """Return whether ``vals`` actually changes a field the approval was granted for."""
        self.ensure_one()
        for fname in self.APPROVAL_RESET_FIELDS:
            if fname not in vals:
                continue
            if fname == 'ordered_qty':
                if float_compare(vals[fname], self.ordered_qty, precision_digits=self.QTY_DIGITS) != 0:
                    return True
            elif fname == 'accepts_partial':
                if bool(vals[fname]) != self.accepts_partial:
                    return True
            elif (vals[fname] or False) != (self.company_id.id or False):
                return True
        return False

    #=== ACTION METHODS ===#

    def action_approve(self):
        """Grant the manager approval allowing a low partial shipment."""
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError(self.env._("Only an approver can approve a delivery request."))
        # Direct method calls must honour the record rules just like an RPC write.
        self.check_access('write')
        for delivery in self:
            if delivery.create_uid == self.env.user:
                raise AccessError(self.env._("A delivery request cannot be approved by its own creator."))
        # Bypasses the write() guard on purpose: this is the only legitimate
        # entry point for the approval, and the rights have just been checked.
        super().write({'approved': True})
        return True

    def action_ship(self):
        """Ship the request when the availability allows it, otherwise block."""
        # Direct method calls must honour the record rules just like an RPC write.
        self.check_access('write')
        to_ship = self.browse()
        for delivery in self:
            if delivery.state != 'draft':
                continue
            delivery._check_shippable()
            to_ship |= delivery
        if to_ship:
            # Bypasses the write() guard on purpose: action_ship is the only
            # transition to the 'done' state, and it has just been validated.
            super(QualityDelivery, to_ship).write({'state': 'done'})
        return True

    #=== BUSINESS METHODS ===#

    def _check_shippable(self):
        """Raise unless the current availability allows the shipment."""
        self.ensure_one()
        digits = self.QTY_DIGITS
        if float_compare(self.available_qty, self.ordered_qty, precision_digits=digits) >= 0:
            return
        if float_compare(self.available_qty, 0.0, precision_digits=digits) <= 0:
            raise ValidationError(self.env._("Nothing is available for this delivery request."))
        if not self.accepts_partial:
            raise ValidationError(
                self.env._("This delivery request does not accept partial shipments.")
            )
        if float_compare(
            self.available_qty, self.PARTIAL_RATIO * self.ordered_qty, precision_digits=digits
        ) >= 0:
            return
        if not self.approved:
            raise ValidationError(
                self.env._("A manager approval is required to ship less than 60% of the ordered quantity.")
            )
