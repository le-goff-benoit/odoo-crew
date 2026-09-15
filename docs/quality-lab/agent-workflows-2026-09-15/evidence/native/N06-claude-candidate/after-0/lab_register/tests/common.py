from odoo.tests import TransactionCase


class LabRegisterCommon(TransactionCase):
    """Two companies, issued and draft records, cancelled lines: the B-42 perimeter."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_main = cls.env['res.company'].create({'name': 'Repair Main'})
        cls.company_other = cls.env['res.company'].create({'name': 'Repair Other'})
        cls.env.user.company_ids = [(6, 0, (cls.company_main + cls.company_other).ids)]
        cls.env.user.company_id = cls.company_main
        cls.env = cls.env(context=dict(
            cls.env.context, allowed_company_ids=(cls.company_main + cls.company_other).ids,
        ))
        cls.Register = cls.env['lab.register']

        cls.draft_late = cls._make_register('LATE', cls.company_main, '2020-01-02', 'draft', 10, 123.0, 'DRAFT-B')
        cls.draft_early = cls._make_register('EARLY', cls.company_main, '2020-01-01', 'draft', 20, 999.0, 'DRAFT-A')
        cls.issued = cls._make_register('ISSUED', cls.company_main, '2019-01-01', 'issued', 17, 555.0, 'ISSUED/005')
        cls.other_draft = cls._make_register('OTHER', cls.company_other, '2020-01-01', 'draft', 80, 666.0, 'OTHER/DRAFT')

    @classmethod
    def _make_register(cls, name, company, date_document, state, sequence, snapshot_total, reference):
        return cls.env['lab.register'].create({
            'name': name,
            'company_id': company.id,
            'date_document': date_document,
            'state': state,
            'sequence': sequence,
            'snapshot_total': snapshot_total,
            'reference': reference,
            'line_ids': [
                (0, 0, {'quantity': 2.0, 'price': 10.0, 'cancelled': False}),
                (0, 0, {'quantity': 5.0, 'price': 99.0, 'cancelled': True}),
            ],
        })

    def assert_untouched(self, record, sequence, snapshot_total, reference, state):
        """Expected values come from the B-42 contract, never from action_repair itself."""
        self.assertEqual(record.sequence, sequence)
        self.assertEqual(record.snapshot_total, snapshot_total)
        self.assertEqual(record.reference, reference)
        self.assertEqual(record.state, state)
