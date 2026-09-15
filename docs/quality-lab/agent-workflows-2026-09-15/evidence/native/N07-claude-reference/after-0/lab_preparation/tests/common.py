from odoo.tests.common import TransactionCase


class LabPreparationCommon(TransactionCase):
    """Jeu de données minimal du modèle de préparation synthétique."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Preparation = cls.env['lab.preparation']

    def new_preparation(self, **values):
        """Crée une préparation en complétant les valeurs obligatoires."""
        return self.Preparation.create({'name': 'P', **values})
