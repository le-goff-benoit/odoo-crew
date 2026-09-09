from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Reprend les dossiers brouillons dont le total inclut des lignes annulées.

    Idempotent : rejouer la migration recalcule les mêmes valeurs. Les dossiers
    validés ne sont pas touchés (D-12), la méthode les ignorant d'elle-même.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    drafts = env['lab.dispatch'].search([('state', '=', 'draft')])
    drafts.action_recalculate()
