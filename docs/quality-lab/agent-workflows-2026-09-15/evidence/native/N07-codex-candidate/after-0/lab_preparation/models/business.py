from odoo import api, fields, models


class LabPreparation(models.Model):
    _name = 'lab.preparation'
    _description = 'Préparation synthétique, distincte du stock standard'

    name = fields.Char(required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done')],
        default='draft', required=True, copy=False,
    )
    ordered_qty = fields.Float()
    delivered_qty = fields.Float(copy=False)
    prepared_qty = fields.Float(copy=False)
    manual = fields.Boolean(copy=False)
    parent_id = fields.Many2one('lab.preparation')

    def action_set_manual(self, quantity):
        """Conserver toute saisie explicite, y compris zéro."""
        self.write({'prepared_qty': quantity, 'manual': True})
        return True

    def action_remainder(self):
        """Créer la demande restante sans modifier la préparation de la source."""
        self.ensure_one()
        remaining_qty = self.ordered_qty - self.delivered_qty
        if remaining_qty <= 0:
            return self.browse()
        remainder = self.copy({
            'name': self.name + ' remainder',
            'ordered_qty': remaining_qty,
            'delivered_qty': 0,
            'prepared_qty': 0,
            'manual': False,
            'state': 'draft',
            'parent_id': self.id,
        })
        self.state = 'done'
        return remainder

    @api.model
    def _cron_prepare(self):
        """Préparer seulement les brouillons automatiques, sans arrondi ajouté."""
        for record in self.search([('state', '=', 'draft'), ('manual', '=', False)]):
            remaining_qty = max(record.ordered_qty - record.delivered_qty, 0)
            if record.prepared_qty != remaining_qty:
                record.prepared_qty = remaining_qty
