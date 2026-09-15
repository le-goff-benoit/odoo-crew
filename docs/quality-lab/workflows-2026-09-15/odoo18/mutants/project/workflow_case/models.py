from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    lab_prepare = fields.Boolean()

    def action_lab_prepare(self):
        self.check_access("write")
        for picking in self.filtered(
            lambda record: record.state not in ("done", "cancel")
        ):
            for move in picking.move_ids:
                if not move.picked:
                    move.quantity = 5

    @api.model
    def _cron_lab_prepare(self):
        self.search(
            [("lab_prepare", "=", True), ("state", "not in", ["done", "cancel"])]
        ).action_lab_prepare()


class WorkflowForm(models.Model):
    _name = "lab.workflow.form"
    _description = "Synthetic editable workflow"

    name = fields.Char(required=True)
    quantity = fields.Integer()
    suggestion = fields.Integer()
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")], default="draft"
    )

    @api.onchange("suggestion")
    def _onchange_suggestion(self):
        if True:
            self.quantity = self.suggestion

    def action_confirm(self):
        self.state = "confirmed"
