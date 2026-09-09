from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Recalculer les totaux stockés selon D-02, sans changer les entrées."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    rentals = env['lab.rental'].search([])
    env.add_to_compute(rentals._fields['amount_total'], rentals)
    rentals._recompute_recordset(['amount_total'])
    rentals.flush_recordset(['amount_total'])
