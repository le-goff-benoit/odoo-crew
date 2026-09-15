from odoo import api, fields, models
from odoo.fields import Domain


class LabPreparation(models.Model):
    _name = 'lab.preparation'
    _description = 'Préparation synthétique, distincte du stock standard'

    name = fields.Char(required=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft', required=True)
    ordered_qty = fields.Float()
    delivered_qty = fields.Float()
    prepared_qty = fields.Float()
    manual = fields.Boolean()
    parent_id = fields.Many2one('lab.preparation')

    def copy_data(self, default=None):
        """Une duplication ouvre une nouvelle demande sans préparation héritée."""
        default = dict(default or {})
        for field, value in {'delivered_qty': 0, 'prepared_qty': 0,
                             'manual': False, 'state': 'draft'}.items():
            default.setdefault(field, value)
        return super().copy_data(default)

    def action_set_manual(self, quantity):
        """Conserver toute saisie explicite, y compris zéro."""
        self.write({'prepared_qty': quantity, 'manual': True})
        return True

    def action_remainder(self):
        """Créer le solde positif et figer la préparation de la source."""
        self.ensure_one()
        remaining_qty = self.ordered_qty - self.delivered_qty
        if remaining_qty <= 0:
            return self.browse()
        remainder = self.copy({
            'name': self.name + ' remainder',
            'ordered_qty': remaining_qty,
            'parent_id': self.id,
        })
        self.state = 'done'
        return remainder

    @api.model
    def _cron_prepare(self):
        """Préparer le solde des seuls brouillons automatiques à recalculer."""
        for record in self.search(Domain('state', '=', 'draft') & Domain('manual', '=', False)):
            quantity = max(record.ordered_qty - record.delivered_qty, 0)
            if record.prepared_qty != quantity:
                record.prepared_qty = quantity
