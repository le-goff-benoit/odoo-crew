from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare


class QualityDelivery(models.Model):
    _name = 'quality_case.delivery'
    _description = 'Synthetic delivery request'

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
        default='draft', required=True, readonly=True,
    )

    #=== CONSTRAINTS ===#

    @api.constrains('ordered_qty', 'available_qty')
    def _check_quantities(self):
        """Validate quantities using the contractual precision."""
        for delivery in self:
            if float_compare(delivery.ordered_qty, 0, precision_digits=6) <= 0:
                raise ValidationError(self.env._(
                    'The ordered quantity must be strictly positive.',
                ))
            if float_compare(delivery.available_qty, 0, precision_digits=6) < 0:
                raise ValidationError(self.env._(
                    'The available quantity cannot be negative.',
                ))

    #=== CRUD ===#

    @api.model_create_multi
    def create(self, vals_list):
        """Create draft requests without allowing approval through defaults."""
        create_vals_list = []
        for vals in vals_list:
            if vals.get('approved') or vals.get('state', 'draft') != 'draft':
                raise AccessError(self.env._(
                    'Approval and shipment must use their dedicated actions.',
                ))
            create_vals_list.append(dict(vals, approved=False, state='draft'))
        return super().create(create_vals_list)

    def write(self, vals):
        """Protect workflow fields and invalidate outdated approvals."""
        self.check_access('write')
        if 'approved' in vals or 'state' in vals:
            raise AccessError(self.env._(
                'Approval and shipment must use their dedicated actions.',
            ))
        if 'company_id' in vals and vals['company_id'] not in self.env.companies.ids:
            raise AccessError(self.env._(
                'The company must be one of your allowed companies.',
            ))

        to_invalidate = self.browse()
        for delivery in self:
            quantity_decreased = (
                'available_qty' in vals
                and float_compare(
                    vals['available_qty'], delivery.available_qty,
                    precision_digits=6,
                ) < 0
            )
            ordered_quantity_changed = (
                'ordered_qty' in vals
                and float_compare(
                    vals['ordered_qty'], delivery.ordered_qty,
                    precision_digits=6,
                ) != 0
            )
            partial_policy_changed = (
                'accepts_partial' in vals
                and bool(vals['accepts_partial']) != delivery.accepts_partial
            )
            company_changed = (
                'company_id' in vals
                and vals['company_id'] != delivery.company_id.id
            )
            if (
                quantity_decreased or ordered_quantity_changed
                or partial_policy_changed or company_changed
            ):
                to_invalidate |= delivery

        # Keep invalidation in the same write as the changed proposal.
        if to_invalidate:
            super(QualityDelivery, to_invalidate).write(dict(vals, approved=False))
        remaining = self - to_invalidate
        if remaining:
            super(QualityDelivery, remaining).write(vals)
        return True

    #=== ACTIONS ===#

    def action_approve(self):
        """Allow an authorized person other than the creator to approve."""
        self.check_access('write')
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError(self.env._(
                'Only an approver can approve a delivery request.',
            ))
        for delivery in self:
            if delivery.create_uid == self.env.user:
                raise AccessError(self.env._(
                    'You cannot approve your own delivery request.',
                ))
            if delivery.state != 'draft':
                raise ValidationError(self.env._(
                    'Only draft delivery requests can be approved.',
                ))
        # Bypass the public workflow-field guard only after authorization.
        return super().write({'approved': True})

    def action_ship(self):
        """Ship only when availability and partial-delivery policy allow it."""
        self.check_access('write')
        self._check_quantities()
        for delivery in self:
            if delivery.state != 'draft':
                raise ValidationError(self.env._(
                    'Only draft delivery requests can be shipped.',
                ))
            if float_compare(delivery.available_qty, 0, precision_digits=6) <= 0:
                raise ValidationError(self.env._(
                    'A delivery cannot be shipped without available quantity.',
                ))
            if float_compare(
                delivery.available_qty, delivery.ordered_qty,
                precision_digits=6,
            ) >= 0:
                continue
            if not delivery.accepts_partial:
                raise ValidationError(self.env._(
                    'The full ordered quantity must be available before shipment.',
                ))
            if (
                float_compare(
                    delivery.available_qty, delivery.ordered_qty * 0.6,
                    precision_digits=6,
                ) < 0
                and not delivery.approved
            ):
                raise ValidationError(self.env._(
                    'Approval is required to ship less than 60% of the ordered quantity.',
                ))
        # Validate the entire recordset before performing the state transition.
        return super().write({'state': 'done'})
