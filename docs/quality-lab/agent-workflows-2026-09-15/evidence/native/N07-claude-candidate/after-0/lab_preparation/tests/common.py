from odoo.tests import TransactionCase


class LabPreparationCommon(TransactionCase):
    """Fixtures for the synthetic preparation model.

    The model depends on `base` only, so there is no business Common to inherit
    from: the helpers below play that role.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Preparation = cls.env['lab.preparation']

    def new_preparation(self, name, **values):
        """Create a preparation, defaults included, and return it."""
        return self.Preparation.create(dict(values, name=name))

    def snapshot(self, preparation):
        """Return the contract fields of a preparation, to compare states."""
        return {
            'state': preparation.state,
            'ordered_qty': preparation.ordered_qty,
            'delivered_qty': preparation.delivered_qty,
            'prepared_qty': preparation.prepared_qty,
            'manual': preparation.manual,
            'parent_id': preparation.parent_id.id,
        }
