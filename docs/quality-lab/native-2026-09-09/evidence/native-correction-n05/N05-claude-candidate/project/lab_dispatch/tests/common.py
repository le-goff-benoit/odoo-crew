from unittest.mock import patch

from odoo import Command
from odoo.tests import TransactionCase


class LabDispatchCommon(TransactionCase):
    """Socle des tests du recalcul : dossiers synthétiques avec lignes actives et annulées."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Dispatch = cls.env['lab.dispatch']

    def _make_dispatch(self, name, state='draft', snapshot=0.0, lines=()):
        """Créer un dossier ; ``lines`` est une suite de tuples (quantité, prix, annulée)."""
        return self.Dispatch.create({
            'name': name,
            'state': state,
            'snapshot_total': snapshot,
            'line_ids': [
                Command.create({'quantity': quantity, 'price': price, 'cancelled': cancelled})
                for quantity, price, cancelled in lines
            ],
        })

    def _written_ids(self, records, action):
        """Exécuter ``action`` en espionnant ``write`` et rendre les ids réellement écrits.

        ``write_date`` ne prouve rien dans un test : elle porte l'horodatage de la
        transaction et reste identique même quand un ``write`` a bien eu lieu.
        """
        written = []
        model_class = type(records)
        original_write = model_class.write

        def spy(self, vals):
            written.extend(self.ids)
            return original_write(self, vals)

        with patch.object(model_class, 'write', spy):
            action()
        return written
