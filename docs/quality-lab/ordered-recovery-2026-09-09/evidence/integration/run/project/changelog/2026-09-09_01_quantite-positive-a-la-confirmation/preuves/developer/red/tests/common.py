from odoo.tests.common import TransactionCase, new_test_user


class LabQualificationCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Exercise the existing internal-user permissions for every new case."""
        super().setUpClass()
        cls.internal_user = new_test_user(
            cls.env, login="qualification_internal", groups="base.group_user",
        )
        cls.Qualification = cls.env["lab.qualification"].with_user(cls.internal_user)

    def assert_record_values(self, record, state, quantity, amount):
        """Read persisted business values after a flush or a rolled-back operation."""
        self.env.flush_all()
        record.invalidate_recordset()
        self.assertEqual(
            (record.state, record.quantity, record.unit_price, record.amount),
            (state, quantity, 10, amount),
        )
