from odoo import api, fields, models


class LabDispatch(models.Model):
    _name = 'lab.dispatch'
    _description = 'Dossier logistique synthétique'

    name = fields.Char(required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('done', 'Validé')], default='draft', required=True)
    snapshot_total = fields.Float()
    line_ids = fields.One2many('lab.dispatch.line', 'dispatch_id')

    #=== ACTIONS ===#

    def action_recalculate(self):
        """Recalculer le total des seuls dossiers brouillons.

        Décision D-12 (``decisions/2026-09-08.md``) : le total d'un brouillon est la
        somme ``quantity × price`` de ses lignes non annulées ; celui d'un dossier
        validé est une photographie définitive, qui n'est ni recalculée ni réécrite.
        Une sélection mixte est donc traitée partiellement, sans lever d'erreur.
        """
        for record in self.filtered(lambda dispatch: dispatch.state == 'draft'):
            record.snapshot_total = record._get_snapshot_total()
        return True

    #=== MÉTIER ===#

    def _get_snapshot_total(self):
        """Rendre le total attendu du dossier : lignes annulées exclues (D-12)."""
        self.ensure_one()
        return sum(
            line.quantity * line.price
            for line in self.line_ids
            if not line.cancelled
        )

    @api.model
    def _repair_draft_snapshots(self):
        """Reprendre les totaux des dossiers brouillons déjà en base, sans toucher aux validés.

        Corriger le calcul ne corrige pas les valeurs déjà stockées : cette reprise est
        appelée par le script de migration. Elle est idempotente parce qu'elle n'écrit
        qu'en cas d'écart réel avec la valeur cible — comparaison stricte, sans tolérance :
        un écart de 0,004 est un écart, et le contrat ne fixe aucun arrondi. Une fois la
        valeur cible écrite, un second passage recalcule la même cible et n'écrit rien.

        :return: les dossiers effectivement repris.
        """
        repaired = self.browse()
        for record in self.search([('state', '=', 'draft')]):
            target = record._get_snapshot_total()
            if record.snapshot_total != target:
                record.snapshot_total = target
                repaired |= record
        return repaired


class LabDispatchLine(models.Model):
    _name = 'lab.dispatch.line'
    _description = 'Ligne synthétique'

    dispatch_id = fields.Many2one('lab.dispatch', required=True, ondelete='cascade')
    quantity = fields.Float()
    price = fields.Float()
    cancelled = fields.Boolean()
