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
        default='draft', required=True, readonly=True,
    )

    #=== CONSTRAINTS ===#

    @api.constrains('ordered_qty', 'available_qty')
    def _check_quantities(self):
        """Validate quantities at the contract's precision."""
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
        """Keep protected fields safe, including against context defaults."""
        vals_list = [dict(vals, approved=False, state='draft') for vals in vals_list]
        with self.env.cr.savepoint():
            deliveries = super().create(vals_list)
            deliveries.check_access('create')
            deliveries._check_quantities()
        return deliveries

    def write(self, vals):
        """Invalidate approval against the immediately preceding proposal."""
        self.check_access('write')
        if 'approved' in vals or 'state' in vals:
            raise AccessError(self.env._(
                'Approval and shipment status can only be changed through their actions.',
            ))

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
        with self.env.cr.savepoint():
            result = super().write(vals)
            # Check the destination company as well as the original records.
            self.check_access('write')
            if to_invalidate:
                super(QualityDelivery, to_invalidate).write({'approved': False})
        return result

    #=== ACTIONS ===#

    def action_approve(self):
        """Approve only with company access and independent authorization."""
        self.check_access('write')
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError(self.env._(
                'Only approvers can approve delivery requests.',
            ))
        if any(delivery.create_uid == self.env.user for delivery in self):
            raise AccessError(self.env._(
                'You cannot approve a delivery request you created.',
            ))
        # Bypass protected-field handling only after checking authorization.
        return super().write({'approved': True})

    def action_ship(self):
        """Ship only accessible draft requests satisfying quantity rules."""
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
                delivery.available_qty, delivery.ordered_qty, precision_digits=6,
            ) >= 0:
                continue
            if not delivery.accepts_partial:
                raise ValidationError(self.env._(
                    'The full ordered quantity must be available before shipment.',
                ))
            if float_compare(
                delivery.available_qty, delivery.ordered_qty * 0.6,
                precision_digits=6,
            ) < 0 and not delivery.approved:
                raise ValidationError(self.env._(
                    'Shipping less than 60 percent requires approval.',
                ))
        # All records are checked before allowing the protected transition.
        return super().write({'state': 'done'})
