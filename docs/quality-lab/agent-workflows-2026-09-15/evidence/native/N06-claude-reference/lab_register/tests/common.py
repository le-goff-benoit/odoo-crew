from odoo.fields import Command
from odoo.tests.common import TransactionCase


class LabRegisterCommon(TransactionCase):
    """Two companies, two ordinary users and a registry mixing drafts and issued references."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env['res.company'].create({'name': 'Register Company A'})
        cls.company_b = cls.env['res.company'].create({'name': 'Register Company B'})

        # An ordinary user working in A while B is also activated: the record rule
        # lets them read both companies, the repair must still only touch A.
        cls.user_multi = cls.env['res.users'].create({
            'name': 'Register Operator',
            'login': 'register_operator',
            'company_id': cls.company_a.id,
            'company_ids': [Command.set([cls.company_a.id, cls.company_b.id])],
            'group_ids': [Command.set([cls.env.ref('base.group_user').id])],
        })
        # An ordinary user who may not even read company B.
        cls.user_single = cls.env['res.users'].create({
            'name': 'Register Clerk',
            'login': 'register_clerk',
            'company_id': cls.company_a.id,
            'company_ids': [Command.set([cls.company_a.id])],
            'group_ids': [Command.set([cls.env.ref('base.group_user').id])],
        })

        # Company A, drafts. EARLY is the oldest; SAME_DATE_1 and SAME_DATE_2 share a
        # date so that the tie is only broken by id.
        cls.draft_early = cls._make_register('A EARLY', cls.company_a, '2024-01-05', 'draft', 20, 999.0, 'DRAFT-EARLY', [(2.0, 10.0, False), (7.0, 3.0, True)])
        cls.draft_same_1 = cls._make_register('A SAME 1', cls.company_a, '2024-01-10', 'draft', 10, 123.0, 'DRAFT-SAME-1', [(3.0, 5.0, False), (1.0, 1000.0, True)])
        cls.draft_same_2 = cls._make_register('A SAME 2', cls.company_a, '2024-01-10', 'draft', 55, 1.0, 'DRAFT-SAME-2', [(4.0, 2.5, False), (2.0, 5.0, False)])
        # Company A, draft left out of every selection: self is the perimeter.
        cls.draft_outside = cls._make_register('A OUTSIDE', cls.company_a, '2024-01-01', 'draft', 42, 777.0, 'DRAFT-OUTSIDE', [(1.0, 1.0, False)])
        # Company A, already issued reference: nothing of it may move.
        cls.issued_a = cls._make_register('A ISSUED', cls.company_a, '2023-01-01', 'issued', 17, 555.0, 'ISSUED/005', [(3.0, 5.0, False), (5.0, 99.0, True)])
        # Company B, draft: another company, strictly untouched.
        cls.draft_b = cls._make_register('B DRAFT', cls.company_b, '2024-01-06', 'draft', 80, 666.0, 'OTHER/DRAFT', [(3.0, 5.0, False), (5.0, 99.0, True)])

    @classmethod
    def _make_register(cls, name, company, date_document, state, sequence, snapshot_total, reference, lines):
        return cls.env['lab.register'].create({
            'name': name,
            'company_id': company.id,
            'date_document': date_document,
            'state': state,
            'sequence': sequence,
            'snapshot_total': snapshot_total,
            'reference': reference,
            'line_ids': [
                Command.create({'quantity': quantity, 'price': price, 'cancelled': cancelled})
                for quantity, price, cancelled in lines
            ],
        })

    def _snapshot(self, records):
        """Return the fields the decision protects, read as superuser to see every company."""
        # sudo() here is the observation instrument of the test, never the code under
        # test: it is the only way to assert that another company stayed untouched.
        return {
            record.id: (record.state, record.sequence, record.snapshot_total, record.reference)
            for record in records.sudo()
        }

    def _as(self, user, records, active_company, activated_companies=None):
        """Return ``records`` as ``user`` would hold them in the web client."""
        companies = activated_companies or [active_company]
        allowed = [active_company.id] + [company.id for company in companies if company != active_company]
        return records.with_user(user).with_context(allowed_company_ids=allowed)
