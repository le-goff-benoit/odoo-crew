# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare

# Amounts up to this value (2 decimals) are paid without a second pair of eyes.
APPROVAL_THRESHOLD = 250.0


class QualityExpense(models.Model):
    _name = 'quality_case.expense'
    _description = 'Synthetic expense request'

    #=== FIELDS ===#

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    amount = fields.Float(required=True)
    approved = fields.Boolean(readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], default='draft', required=True, readonly=True)

    #=== CONSTRAINT METHODS ===#

    @api.constrains('amount')
    def _check_amount(self):
        """Only a strictly positive amount, at two decimals, may be claimed."""
        for expense in self:
            if float_compare(expense.amount, 0.0, precision_digits=2) <= 0:
                raise ValidationError(self.env._("The amount of %(name)s must be strictly positive.", name=expense.name))

    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        # `approved` and `state` are server-controlled: neither an RPC payload
        # nor the `default_*` keys of the context may seed them.
        for vals in vals_list:
            vals['approved'] = False
            vals['state'] = 'draft'
        return super().create(vals_list)

    def write(self, vals):
        # Same reason as in `create`: those two fields only move through the
        # `action_*` methods, which check the authorization server-side.
        vals = {fname: value for fname, value in vals.items() if fname not in ('approved', 'state')}
        to_invalidate = self.browse()
        if 'amount' in vals or 'company_id' in vals:
            for expense in self:
                if not expense.approved:
                    continue
                # A raise invalidates the approval; a decrease or an identical
                # rewrite keeps it. Switching company invalidates it too.
                if 'amount' in vals and float_compare(vals['amount'], expense.amount, precision_digits=2) > 0:
                    to_invalidate |= expense
                elif 'company_id' in vals and vals['company_id'] != expense.company_id.id:
                    to_invalidate |= expense
        res = super().write(vals)
        if to_invalidate:
            super(QualityExpense, to_invalidate).write({'approved': False})
        return res

    #=== ACTION METHODS ===#

    def action_approve(self):
        """Grant the approval required to pay an amount above the threshold."""
        self.check_access('write')
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError(self.env._("Only an approver may approve an expense request."))
        for expense in self:
            if expense.create_uid == self.env.user:
                raise AccessError(self.env._("You cannot approve your own expense request."))
        # Bypasses the guard of `write`, which is exactly what this method is for.
        super().write({'approved': True})
        return True

    def action_pay(self):
        """Move a draft request to paid, checking the approval when required."""
        self.check_access('write')
        for expense in self:
            if expense.state != 'draft':
                raise ValidationError(self.env._("Only a draft expense request can be paid."))
            if float_compare(expense.amount, APPROVAL_THRESHOLD, precision_digits=2) > 0 and not expense.approved:
                raise AccessError(self.env._(
                    "An expense request above %(threshold)s requires the approval of another approver.",
                    threshold=APPROVAL_THRESHOLD,
                ))
        super().write({'state': 'paid'})
        return True
