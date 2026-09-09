from odoo import api, fields, models


class LabDispatch(models.Model):
    _name = 'lab.dispatch'
    _description = 'Dossier logistique synthétique'

    name = fields.Char(required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('done', 'Validé')], default='draft', required=True)
    snapshot_total = fields.Float()
    line_ids = fields.One2many('lab.dispatch.line', 'dispatch_id')

    def _snapshot_amount(self):
        """Montant attendu du dossier : les lignes annulées ne comptent pas (D-12, Q2)."""
        self.ensure_one()
        return sum(line.quantity * line.price for line in self.line_ids if not line.cancelled)

    def action_recalculate(self):
        """Recalcule le total des seuls brouillons.

        D-12 (Q1) : un dossier validé est définitivement figé. Le filtrage est fait
        avant la boucle, et non dedans : réécrire la même valeur resterait une écriture.
        Une sélection mixte est acceptée sans erreur, les validés sont simplement ignorés.
        """
        for record in self.filtered(lambda dispatch: dispatch.state == 'draft'):
            record.snapshot_total = record._snapshot_amount()
        return True

    @api.model
    def _reprise_snapshot_brouillons(self):
        """Redresse les totaux stockés des brouillons existants et rend ceux qui ont bougé.

        Idempotente : la valeur n'est écrite que si elle diffère de celle en base, donc une
        seconde exécution ne modifie rien. La comparaison est exacte parce que
        `snapshot_total` est un `Float()` sans `digits` : aucun arrondi n'est appliqué, la
        valeur relue après écriture est identique à celle écrite, et une comparaison
        arrondie laisserait passer les dérives fines (cas réel : 20.004 au lieu de 20.0).
        """
        reprises = self.browse()
        for record in self.search([('state', '=', 'draft')]):
            montant = record._snapshot_amount()
            if record.snapshot_total != montant:
                record.snapshot_total = montant
                reprises |= record
        return reprises


class LabDispatchLine(models.Model):
    _name = 'lab.dispatch.line'
    _description = 'Ligne synthétique'

    dispatch_id = fields.Many2one('lab.dispatch', required=True, ondelete='cascade')
    quantity = fields.Float()
    price = fields.Float()
    cancelled = fields.Boolean()
