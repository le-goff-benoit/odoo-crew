from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Reprend les préparations automatiques encore en brouillon.

    Corriger le calcul ne corrige pas les valeurs déjà en base. La reprise
    autorisée par la décision N-17 est exactement le recalcul du cron : il ne
    touche ni les saisies manuelles, ni les préparations terminées.
    """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['lab.preparation']._cron_prepare()
