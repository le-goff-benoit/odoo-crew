from odoo import api, fields, models


class LabQualification(models.Model):
    _name = "lab.qualification"
    _description = "Synthetic quantity qualification"

    _quantity_nonnegative = models.Constraint("CHECK(quantity >= 0)", "Quantity must be nonnegative.")
    _confirmed_quantity_positive = models.Constraint(
        "CHECK(state != 'confirmed' OR quantity > 0)",
        "A confirmed record must have a strictly positive quantity.",
    )

    name = fields.Char(required=True)
    quantity = fields.Integer(default=0)
    unit_price = fields.Float(default=10)
    amount = fields.Float(compute="_compute_amount", store=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")], default="draft"
    )

    @api.depends("quantity", "unit_price")
    def _compute_amount(self):
        """Compute the amount from the current quantity and unit price."""
        for record in self:
            record.amount = record.quantity * record.unit_price

    def action_confirm(self):
        """Confirm the selected records in one operation."""
        self.write({"state": "confirmed"})
