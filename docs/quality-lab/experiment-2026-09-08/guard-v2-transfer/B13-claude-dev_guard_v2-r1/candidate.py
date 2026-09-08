# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare

# Amounts up to this value (2 decimals) are payable without a second pair of eyes.
APPROVAL_THRESHOLD = 250.0

# Never writable through create/write, whatever the caller or the context defaults.
PROTECTED_FIELDS = ('approved', 'state')


class QualityExpense(models.Model):
    _name = 'quality_case.expense'
    _description = 'Synthetic expense request'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    amount = fields.Float(required=True)
    approved = fields.Boolean(readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], default='draft', required=True, readonly=True)

    #=== CONSTRAINT METHODS ===#

    @api.constrains('amount')
    def _check_amount(self):
        """An expense request covers a single strictly positive amount."""
        for expense in self:
            if float_compare(expense.amount, 0.0, precision_digits=2) <= 0:
                raise ValidationError(self.env._("The amount of %(name)s must be strictly positive.", name=expense.name))

    #=== CRUD METHODS ===#

    @api.model_create_multi
    def create(self, vals_list):
        # The protected values are forced in every dict: dropping the keys would
        # not be enough, since create() applies default_* from the context to the
        # fields left out of vals.
        for vals in vals_list:
            vals['approved'] = False
            vals['state'] = 'draft'
        return super().create(vals_list)

    def write(self, vals):
        vals = {key: value for key, value in vals.items() if key not in PROTECTED_FIELDS}
        if not vals:
            return True
        # The approval is given for one amount and one company: it is compared to
        # the value stored right before this write, not to any earlier one.
        to_invalidate = self.browse()
        if 'amount' in vals or 'company_id' in vals:
            for expense in self:
                if not expense.approved:
                    continue
                if 'amount' in vals and float_compare(vals['amount'], expense.amount, precision_digits=2) > 0:
                    to_invalidate |= expense
                elif 'company_id' in vals and vals['company_id'] != expense.company_id.id:
                    to_invalidate |= expense
        result = super().write(vals)
        if to_invalidate:
            to_invalidate._set_protected({'approved': False})
        return result

    #=== ACTION METHODS ===#

    def action_approve(self):
        """Grant the second-pair-of-eyes approval required above the threshold."""
        # Authorization is checked server-side: ACL and company rules apply even
        # on a direct RPC call to this method.
        self.check_access('write')
        if not self.env.user.has_group('quality_case.group_approver'):
            raise AccessError(self.env._("Only an approver can approve an expense request."))
        for expense in self:
            if expense.create_uid == self.env.user:
                raise AccessError(self.env._("You cannot approve your own expense request."))
        self._set_protected({'approved': True})
        return True

    def action_pay(self):
        """Move a draft request to paid, requiring an approval above the threshold."""
        self.check_access('write')
        for expense in self:
            if expense.state != 'draft':
                raise ValidationError(self.env._("Only a draft expense request can be paid."))
            if float_compare(expense.amount, APPROVAL_THRESHOLD, precision_digits=2) > 0 and not expense.approved:
                raise ValidationError(self.env._(
                    "An expense request above %(threshold)s must be approved before payment.",
                    threshold=APPROVAL_THRESHOLD,
                ))
        self._set_protected({'state': 'paid'})
        return True

    #=== BUSINESS METHODS ===#

    def _set_protected(self, vals):
        """Write the protected fields, bypassing the write() guard.

        Private on purpose: not reachable over RPC, so `approved` and `state`
        can only change through the actions that check the authorization.
        """
        return super().write(vals)
