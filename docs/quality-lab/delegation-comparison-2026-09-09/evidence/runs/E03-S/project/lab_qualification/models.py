from odoo import api, fields, models


class LabQualification(models.Model):
    _name = "lab.qualification"
    _description = "Synthetic quantity qualification"

    _quantity_nonnegative = models.Constraint(
        "CHECK(quantity >= 0)", "Quantity must be nonnegative."
    )
    _unit_price_nonnegative = models.Constraint(
        "CHECK(unit_price >= 0)", "Unit price must be nonnegative."
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
        for record in self:
            record.amount = record.quantity * record.unit_price

    def action_confirm(self):
        self.write({"state": "confirmed"})
