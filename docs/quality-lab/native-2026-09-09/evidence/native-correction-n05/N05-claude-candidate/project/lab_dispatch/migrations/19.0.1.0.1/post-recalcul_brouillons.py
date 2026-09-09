"""Reprise des totaux des dossiers brouillons déjà en base (décision D-12 du 2026-09-08).

Jusqu'à la 19.0.1.0.0, ``action_recalculate`` additionnait aussi les lignes annulées et
écrasait les dossiers validés. Corriger la méthode ne corrige pas les valeurs déjà
stockées : cette reprise les remet à la valeur du contrat, pour les seuls brouillons.
Elle est idempotente et peut être rejouée sans effet.
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    repaired = env['lab.dispatch']._repair_draft_snapshots()
    _logger.info(
        "lab_dispatch : reprise des totaux de brouillons — %s dossier(s) repris %s",
        len(repaired), repaired.mapped('name'),
    )
