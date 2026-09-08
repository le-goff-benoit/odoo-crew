# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

# Quantities are compared with six decimals, as stated by the specification.
QTY_DIGITS = 6
# Minimum served ratio (inclusive) allowing a partial shipping without approval.
PARTIAL_RATIO_WITHOUT_APPROVAL = 0.6
# Fields whose modification always invalidates a previously granted approval.
APPROVAL_INVALIDATING_FIELDS = ('ordered_qty', 'accepts_partial', 'company_id')
# Fields that may only be set by their dedicated action, never through create/write.
PROTECTED_FIELDS = ('approved', 'state')


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

    #=== CONSTRAINT METHODS ===#

    @api.constrains('ordered_qty', 'available_qty')
    def _check_quantities(self):
        """Ordered quantity is strictly positive, available quantity is never negative."""
        for delivery in self:
            if float_compare(delivery.ordered_qty, 0.0, precision_digits=QTY_DIGITS) <= 0:
                raise ValidationError(self.env._("The ordered quantity must be strictly positive."))
            if float_compare(delivery.available_qty, 0.0, precision_digits=QTY_DIGITS) < 0:
                raise ValidationError(self.env._("The available quantity cannot be negative."))

    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        """Force the protected fields to their safe value.

        Stripping the keys would not be enough: ``default_approved`` and
        ``default_state`` in the context are applied by ``super()`` for the
        fields missing from the values, so they are set explicitly instead.
        """
        vals_list = [dict(vals, approved=False, state='draft') for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        """Ignore writes on the protected fields and invalidate stale approvals."""
        vals = {key: value for key, value in vals.items() if key not in PROTECTED_FIELDS}
        to_invalidate = self.browse()
        for delivery in self.filtered('approved'):
            if delivery._is_approval_invalidated(vals):
                to_invalidate |= delivery
        res = super().write(vals)
        if to_invalidate:
            # Bypasses the sanitizing above, which would drop the key.
            super(QualityDelivery, to_invalidate).write({'approved': False})
        return res

    #=== ACTION METHODS ===#

    def action_approve(self):
        """Grant the manager approval required by a low partial shipping."""
        self.check_access('write')
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError(self.env._("Only an approver can approve a delivery request."))
        for delivery in self:
            if delivery.create_uid.id == self.env.uid:
                raise AccessError(self.env._("A delivery request cannot be approved by its own creator."))
        # Bypasses the sanitizing of write(): this is the only legitimate writer.
        super().write({'approved': True})
        return True

    def action_ship(self):
        """Ship the requests whose availability satisfies the shipping policy."""
        self.check_access('write')
        for delivery in self:
            delivery._check_shippable()
        # Bypasses the sanitizing of write(): this is the only legitimate writer.
        super().write({'state': 'done'})
        return True

    #=== BUSINESS METHODS ===#

    def _is_approval_invalidated(self, vals):
        """Return whether the values about to be written void the current approval."""
        self.ensure_one()
        if 'ordered_qty' in vals and float_compare(vals['ordered_qty'], self.ordered_qty, precision_digits=QTY_DIGITS) != 0:
            return True
        if 'accepts_partial' in vals and bool(vals['accepts_partial']) != self.accepts_partial:
            return True
        if 'company_id' in vals and (vals['company_id'] or False) != (self.company_id.id or False):
            return True
        # Only a decrease of the immediately previous proposal voids the approval.
        if 'available_qty' in vals and float_compare(vals['available_qty'], self.available_qty, precision_digits=QTY_DIGITS) < 0:
            return True
        return False

    def _check_shippable(self):
        """Raise unless the request may be shipped with its current availability."""
        self.ensure_one()
        if float_compare(self.available_qty, self.ordered_qty, precision_digits=QTY_DIGITS) >= 0:
            return
        if float_is_zero(self.available_qty, precision_digits=QTY_DIGITS):
            raise ValidationError(self.env._("Nothing is available for %(name)s.", name=self.name))
        if not self.accepts_partial:
            raise ValidationError(
                self.env._("%(name)s does not accept a partial shipping: wait for the full quantity.", name=self.name)
            )
        threshold = PARTIAL_RATIO_WITHOUT_APPROVAL * self.ordered_qty
        if float_compare(self.available_qty, threshold, precision_digits=QTY_DIGITS) >= 0:
            return
        if not self.approved:
            raise ValidationError(
                self.env._("A manager approval is required to ship %(name)s below 60%% of the ordered quantity.", name=self.name)
            )
