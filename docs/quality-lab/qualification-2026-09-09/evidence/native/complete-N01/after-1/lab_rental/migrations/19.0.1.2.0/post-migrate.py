from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Recompute the stored total of every rental after decision D-03.

    Changing the body of a compute method does not refresh a stored field, and
    the 19.0.1.1.0 script is not replayed on a database that already went
    through it: without this one, a copy upgraded under D-02 would keep the
    12 EUR fee from four days.

    The recomputation derives the total from days, daily rate and kind and
    writes nothing else, so it is idempotent and symmetric: it removes the fee
    from four-day rentals — whose total goes down — just as it raises it to
    15 EUR on the longer ones.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    rentals = env['lab.rental'].search([])
    env.add_to_compute(rentals._fields['amount_total'], rentals)
    env.flush_all()
