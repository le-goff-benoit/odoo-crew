from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Reprendre les totaux déjà en base après l'entrée en vigueur de D-03.

    `amount_total` est un champ stocké : changer la formule de son compute ne
    réécrit pas les lignes existantes. La reprise de D-02
    (`migrations/19.0.1.1.0/`) ne peut pas servir ici — elle ne s'exécute que
    pour une base encore en 19.0.1.0.0, et reste donc en place pour celles-là.

    Particularité de D-03 : la correction va **dans les deux sens**. Les
    locations de cinq jours et plus gagnent 3 EUR (12 -> 15), mais celles de
    quatre jours perdent les 12 EUR que D-02 leur avait ajoutés. On ne calcule
    donc aucun delta : on réapplique la formule courante, seule forme correcte
    et seule forme idempotente.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    rentals = env['lab.rental'].search([])
    rentals._compute_amount_total()
    rentals.flush_recordset(['amount_total'])
