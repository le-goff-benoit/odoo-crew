"""Reprise D-02 à exécuter dans odoo shell après mise à jour de lab_rental.

Portée : tous les essais lab.rental, conformément à decisions/2026-09-08.md.
Idempotente : recalcule depuis les entrées, sans cumuler les frais.
Dans ce laboratoire : /bridge/labctl shell <chemin absolu de ce fichier>.
Toute livraison ultérieure doit intégrer explicitement cette étape de reprise.
"""

import logging


_logger = logging.getLogger(__name__)
rentals = env['lab.rental'].search([])
env.add_to_compute(rentals._fields['amount_total'], rentals)
rentals._recompute_recordset(['amount_total'])
rentals.flush_recordset(['amount_total'])
env.cr.commit()
_logger.info('D-02 : %s totaux de locations/prêts recalculés.', len(rentals))
