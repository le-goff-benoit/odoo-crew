from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Recompute the stored total of the rentals already in database.

    Changing the body of a compute method does not refresh a stored field: an
    upgrade alone would leave the rentals booked before decision D-02 without
    their preparation fee. The recomputation is idempotent — it derives the
    total from days, daily rate and kind, and writes nothing else.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    rentals = env['lab.rental'].search([])
    env.add_to_compute(rentals._fields['amount_total'], rentals)
    env.flush_all()
