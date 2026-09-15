from odoo import fields, models


class LabRegister(models.Model):
    _name = 'lab.register'
    _description = 'Registre synthétique'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    date_document = fields.Date(required=True)
    state = fields.Selection([('draft', 'Draft'), ('issued', 'Issued')], default='draft', required=True)
    sequence = fields.Integer(default=10)
    reference = fields.Char()
    snapshot_total = fields.Float()
    line_ids = fields.One2many('lab.register.line', 'register_id')

    #=== ACTIONS ===#

    def action_repair(self):
        """Renumber and recompute the draft records of the active company (decision B-42).

        Only the drafts of ``self`` belonging to ``env.company`` are repaired: a mixed
        selection is allowed, issued references and other companies are left as they
        are. Sequences are rewritten from scratch (100, 200, ...) so that replaying the
        repair yields the same values.
        """
        repairable = self.filtered(
            lambda record: record.state == 'draft' and record.company_id == self.env.company,
        )
        for index, record in enumerate(repairable.sorted(lambda record: (record.date_document, record.id)), 1):
            record.write({
                'sequence': index * 100,
                'snapshot_total': sum(
                    line.quantity * line.price for line in record.line_ids if not line.cancelled
                ),
            })
        return True


class LabRegisterLine(models.Model):
    _name = 'lab.register.line'
    _description = 'Ligne de registre synthétique'

    register_id = fields.Many2one('lab.register', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='register_id.company_id', store=True)
    quantity = fields.Float()
    price = fields.Float()
    cancelled = fields.Boolean()
