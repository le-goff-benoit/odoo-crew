# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare

QTY_PRECISION_DIGITS = 6
PARTIAL_SHIPPING_THRESHOLD = 0.6


class QualityDelivery(models.Model):
    _name = 'quality_case.delivery'
    _description = 'Synthetic delivery request'

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
        """A request covers a single article: order something, hold nothing negative."""
        for delivery in self:
            if float_compare(delivery.ordered_qty, 0.0, precision_digits=QTY_PRECISION_DIGITS) <= 0:
                raise ValidationError(self.env._("The ordered quantity must be strictly positive."))
            if float_compare(delivery.available_qty, 0.0, precision_digits=QTY_PRECISION_DIGITS) < 0:
                raise ValidationError(self.env._("The available quantity cannot be negative."))

    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        # `approved` and `state` are only granted by `action_approve` / `action_ship`:
        # they are dropped here so that they can neither be forged nor carried over by a copy.
        for vals in vals_list:
            vals.pop('approved', None)
            vals.pop('state', None)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get('quality_case_privileged_write'):
            self._check_workflow_values(vals)
        invalidated = self.filtered(lambda delivery: delivery.approved and delivery._is_approval_invalidated_by(vals))
        res = super().write(vals)
        if invalidated:
            # Bypass this override: the reset is a consequence of the workflow, not a forgery.
            super(QualityDelivery, invalidated).write({'approved': False})
        return res

    #=== ACTION METHODS ===#

    def action_approve(self):
        """Record the approver agreement allowing a partial shipment below the threshold."""
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError(self.env._("Only a delivery approver can approve a request."))
        # Direct calls must honour the record rules just like a write from the interface does.
        self.check_access('write')
        for delivery in self:
            if delivery.create_uid == self.env.user:
                raise AccessError(self.env._(
                    "The request %(name)s cannot be approved by the user who created it.",
                    name=delivery.name,
                ))
        self.with_context(quality_case_privileged_write=True).write({'approved': True})
        return True

    def action_ship(self):
        """Ship the request when the available quantity honours the shipping policy."""
        self.check_access('write')
        for delivery in self:
            delivery._check_shipping_allowed()
        self.with_context(quality_case_privileged_write=True).write({'state': 'done'})
        return True

    #=== BUSINESS METHODS ===#

    def _check_workflow_values(self, vals):
        """Forbid any direct assignment of the fields driven by the workflow actions."""
        if 'approved' in vals and any(delivery.approved != bool(vals['approved']) for delivery in self):
            raise AccessError(self.env._("The approval can only be granted through the approval action."))
        if 'state' in vals and any(delivery.state != vals['state'] for delivery in self):
            raise AccessError(self.env._("The state can only be changed through the shipping action."))

    def _is_approval_invalidated_by(self, vals):
        """Return whether `vals` breaks the proposal the approver agreed on.

        Only the immediately preceding proposal matters: a lower available quantity voids
        the agreement, a higher one keeps it, and no implicit historical maximum is kept.
        """
        self.ensure_one()
        if 'ordered_qty' in vals and float_compare(
            float(vals['ordered_qty'] or 0.0), self.ordered_qty, precision_digits=QTY_PRECISION_DIGITS
        ) != 0:
            return True
        if 'accepts_partial' in vals and bool(vals['accepts_partial']) != self.accepts_partial:
            return True
        if 'company_id' in vals:
            company_id = vals['company_id']
            if isinstance(company_id, models.BaseModel):
                company_id = company_id.id
            if (company_id or False) != self.company_id.id:
                return True
        if 'available_qty' in vals and float_compare(
            float(vals['available_qty'] or 0.0), self.available_qty, precision_digits=QTY_PRECISION_DIGITS
        ) < 0:
            return True
        return False

    def _check_shipping_allowed(self):
        """Raise unless the current proposal may be shipped as it stands."""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(self.env._("The request %(name)s has already been shipped.", name=self.name))
        if float_compare(self.available_qty, 0.0, precision_digits=QTY_PRECISION_DIGITS) <= 0:
            raise ValidationError(self.env._("Nothing is available for the request %(name)s.", name=self.name))
        if float_compare(self.available_qty, self.ordered_qty, precision_digits=QTY_PRECISION_DIGITS) >= 0:
            return
        if not self.accepts_partial:
            raise ValidationError(self.env._(
                "The request %(name)s does not accept a partial shipment and must wait for the full quantity.",
                name=self.name,
            ))
        if float_compare(
            self.available_qty,
            self.ordered_qty * PARTIAL_SHIPPING_THRESHOLD,
            precision_digits=QTY_PRECISION_DIGITS,
        ) < 0 and not self.approved:
            raise ValidationError(self.env._(
                "The request %(name)s ships less than 60%% of the ordered quantity and requires an approval.",
                name=self.name,
            ))
