from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Recalculer les totaux déjà en base après l'entrée en vigueur de D-02.

    `amount_total` est un champ stocké : changer la formule de son compute ne
    réécrit pas les lignes existantes, seules les écritures ultérieures les
    recalculent. Sans cette reprise, une location de quatre jours enregistrée
    avant la mise à jour garderait un total sans frais de préparation.

    Le recalcul est idempotent : il réapplique la formule courante et peut être
    rejoué sans dériver.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    rentals = env['lab.rental'].search([])
    rentals._compute_amount_total()
    rentals.flush_recordset(['amount_total'])
