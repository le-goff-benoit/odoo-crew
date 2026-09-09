"""Recalculer D-03 après mise à jour, sur la copie synthétique autorisée.

Exécution : /bridge/labctl shell /work/changelog/2026-09-09_01_frais-de-preparation-des-locations/recompute_totals.py
La version reste inchangée jusqu'à la clôture ; ce script est à rejouer
explicitement après la mise à jour, qui ne suffit pas à reprendre un compute.
"""
import logging


records = env['lab.rental'].search([])
before = records.mapped('amount_total')
env.add_to_compute(records._fields['amount_total'], records)
records._recompute_recordset(['amount_total'])
records.flush_recordset(['amount_total'])
records.invalidate_recordset(['amount_total'])
after = records.mapped('amount_total')
logging.getLogger(__name__).info(
    'D-03 : %s essais recalculés, %s totaux modifiés',
    len(records), sum(old != new for old, new in zip(before, after)),
)
env.cr.commit()
