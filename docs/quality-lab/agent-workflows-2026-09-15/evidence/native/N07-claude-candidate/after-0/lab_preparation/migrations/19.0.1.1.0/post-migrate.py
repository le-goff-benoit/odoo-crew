from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Recompute the automatic drafts left with a stale prepared quantity.

    Fixing `_cron_prepare` does not fix the values already stored, so the very
    same method is replayed here: manual entries — zero included — and done
    preparations stay untouched, and a second run changes nothing.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['lab.preparation']._cron_prepare()
