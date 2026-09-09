import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Reprise des totaux stockés sur les dossiers brouillons existants (D-12).

    Les dossiers validés ne sont pas touchés. La reprise est idempotente : la rejouer
    ne modifie plus rien.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    reprises = env['lab.dispatch']._reprise_snapshot_brouillons()
    _logger.info("lab_dispatch : reprise des brouillons, %s dossier(s) corrigé(s)", len(reprises))
