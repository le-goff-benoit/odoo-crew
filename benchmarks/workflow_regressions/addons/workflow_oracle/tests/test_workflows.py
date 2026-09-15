import logging
from contextlib import ExitStack
from unittest.mock import patch
from pathlib import Path
import subprocess

from odoo import Command, fields
from odoo.exceptions import AccessError
from odoo.tests import tagged, new_test_user
from odoo.tests.common import TransactionCase, HttpCase
from odoo.addons.account.tests.common import AccountTestInvoicingCommon

from .pdf_assertions import accounting_write, assert_pdf_cohort

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestStockWorkflow(TransactionCase):
    def test_partial_then_cron_real_rights(self):
        user = new_test_user(
            self.env, login="warehouse_lab", groups="stock.group_stock_user"
        )
        portal = new_test_user(self.env, login="portal_lab", groups="base.group_portal")
        product = self.env["product.product"].create(
            {"name": "Synthetic parcel", "is_storable": True}
        )
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        source = warehouse.lot_stock_id
        target = self.env.ref("stock.stock_location_customers")
        self.env["stock.quant"]._update_available_quantity(product, source, 5)
        picking = (
            self.env["stock.picking"]
            .with_user(user)
            .create(
                {
                    "picking_type_id": warehouse.out_type_id.id,
                    "location_id": source.id,
                    "location_dest_id": target.id,
                    "lab_prepare": True,
                    "move_ids": [
                        Command.create(
                            {
                                "product_id": product.id,
                                "product_uom_qty": 5,
                                "product_uom": product.uom_id.id,
                                "location_id": source.id,
                                "location_dest_id": target.id,
                            }
                        )
                    ],
                }
            )
        )
        picking.action_confirm()
        picking.action_assign()
        picking.action_lab_prepare()
        self.assertEqual(picking.move_ids.quantity, 5)
        picking.move_ids.write({"quantity": 2, "picked": True})
        picking.with_context(skip_backorder=True).button_validate()
        backorder = (
            self.env["stock.picking"]
            .with_user(user)
            .search([("backorder_id", "=", picking.id)])
        )
        self.assertEqual(len(backorder), 1)
        self.assertEqual(backorder.move_ids.product_uom_qty, 3)
        cron = self.env["ir.cron"].create(
            {
                "name": "Synthetic preparation",
                "model_id": self.env.ref("stock.model_stock_picking").id,
                "state": "code",
                "code": "model._cron_lab_prepare()",
                "user_id": user.id,
                "interval_number": 1,
                "interval_type": "days",
            }
        )
        with self.enter_registry_test_mode():
            self.assertTrue(cron.method_direct_trigger() is True)
        backorder.invalidate_recordset()
        self.assertEqual(backorder.move_ids.quantity, 3, "WORKFLOW_STOCK_REMAINDER")
        self.assertEqual(picking.move_ids.quantity, 2)
        self.assertEqual(picking.state, "done")
        with self.assertRaises(AccessError):
            backorder.with_user(portal).action_lab_prepare()
        _logger.info("WORKFLOW_PASS stock")


@tagged("post_install", "-at_install")
class TestInvoiceWorkflow(AccountTestInvoicingCommon, HttpCase):
    def _accounting_snapshot(self, move):
        snapshot = {}
        for table, condition in (("account_move", "id"), ("account_move_line", "move_id")):
            self.env.cr.execute(
                f"SELECT to_jsonb(row) FROM {table} row WHERE {condition} = %s ORDER BY id",
                [move.id],
            )
            snapshot[table] = self.env.cr.fetchall()
        return snapshot

    def test_historical_invoice_pdf(self):
        self.env["res.lang"]._activate_lang("fr_FR")
        invoice_user = new_test_user(
            self.env,
            login="invoice_lab",
            groups="account.group_account_invoice",
            company_id=self.env.company.id,
            company_ids=[Command.set(self.env.company.ids)],
            lang="en_US",
        )
        self.assertFalse(invoice_user.has_group("base.group_system"))
        output = Path("/tmp/workflow-evidence")
        output.mkdir(exist_ok=True)
        cohorts = (
            ("current-invoice", "out_invoice", fields.Date.today(), "fr_FR", "en_US", "Facture"),
            ("historical-invoice", "out_invoice", fields.Date.from_string("2020-02-03"), "fr_FR", "en_US", "Facture"),
            ("credit-note", "out_refund", fields.Date.today(), "en_US", "fr_FR", "Credit Note"),
        )
        completed_cohorts = 0
        for cohort, move_type, date, recipient_language, user_language, title in cohorts:
            with self.subTest(cohort=cohort):
                partner = self.partner_a.copy({"name": "Synthetic recipient " + cohort, "lang": recipient_language})
                invoice_user.lang = user_language
                lines = [
                    ("Prestation " + cohort, 7, True),
                    ("Forfait convenu", 42, False),
                    ("Explication gratuite", 0, False),
                    ("Marqueur technique masque", 0, True),
                ]
                move = self.env["account.move"].create({
                    "move_type": move_type,
                    "partner_id": partner.id,
                    "invoice_date": date,
                    "invoice_line_ids": [Command.create({
                        "name": label, "quantity": 1, "price_unit": price,
                        "tax_ids": [Command.clear()],
                        "account_id": self.company_data["default_account_revenue"].id,
                        "lab_technical_zero": technical,
                    }) for label, price, technical in lines],
                })
                move.action_post()
                self.assertEqual(move.state, "posted")
                self.assertEqual(move.amount_total, 49)
                self.assertEqual(len(move.invoice_line_ids), 4)
                self.env.flush_all()
                before = self._accounting_snapshot(move)
                original_execute = type(self.env.cr).execute

                def checked_execute(cursor, query, *args, **kwargs):
                    if accounting_write(query):
                        raise AssertionError("WORKFLOW_INVOICE_ACCOUNTING_WRITE SQL")
                    return original_execute(cursor, query, *args, **kwargs)

                with ExitStack() as guards:
                    for model in ("account.move", "account.move.line"):
                        for operation in ("create", "write", "unlink"):
                            guards.enter_context(patch.object(
                                type(self.env[model]), operation,
                                side_effect=AssertionError("WORKFLOW_INVOICE_ACCOUNTING_WRITE " + model + "." + operation),
                            ))
                    guards.enter_context(patch.object(type(self.env.cr), "execute", checked_execute))
                    pdf, _ = (
                        self.env["ir.actions.report"].with_user(invoice_user)
                        .with_context(lang=user_language, force_report_rendering=True)
                        ._render_qweb_pdf("account.account_invoices", [move.id])
                    )
                    self.env.flush_all()
                self.assertEqual(self._accounting_snapshot(move), before, "WORKFLOW_INVOICE_ACCOUNTING_SNAPSHOT")
                self.assertTrue(pdf.startswith(b"%PDF"))
                (output / (cohort + ".pdf")).write_bytes(pdf)
                rendered = subprocess.run(
                    ["pdftotext", "-", "-"], input=pdf, capture_output=True, check=True
                ).stdout.decode()
                (output / (cohort + ".txt")).write_text(rendered)
                assert_pdf_cohort(rendered, [label for label, _, _ in lines[:3]], [lines[3][0]], title)
                completed_cohorts += 1
                _logger.info("WORKFLOW_PDF_COHORT %s recipient=%s user=%s ordinary_user=true accounting_unchanged=true", cohort, recipient_language, user_language)
        if completed_cohorts == len(cohorts):
            _logger.info("WORKFLOW_PASS invoice_pdf")


@tagged("post_install", "-at_install")
class TestFormWorkflow(HttpCase):
    def test_explicit_value_survives_browser(self):
        record = self.env["lab.workflow.form"].create(
            {"name": "Browser explicit value", "quantity": 7, "suggestion": 2}
        )
        action = self.env.ref("workflow_case.form_action")
        self.browser_js(
            f"/odoo/action-{action.id}/{record.id}",
            r"""
        (async () => {
          const wait = async f => {for (let i=0;i<200;i++) {if(f()) return f(); await new Promise(r=>setTimeout(r,100));} throw Error('Expected form state missing');};
          const input = await wait(()=>document.querySelector('.o_field_widget[name="suggestion"] input'));
          input.value='9'; input.dispatchEvent(new Event('input',{bubbles:true})); input.dispatchEvent(new Event('change',{bubbles:true})); input.blur();
          await new Promise(r=>setTimeout(r,700));
          const quantity = document.querySelector('.o_field_widget[name="quantity"] input');
          if (quantity.value !== '7') throw Error('WORKFLOW_FORM_EXPLICIT_VALUE '+quantity.value);
          document.querySelector('button[name="action_confirm"]').click();
          await wait(()=>document.querySelector('.o_statusbar_status button[data-value="confirmed"].o_arrow_button_current'));
          console.log('WORKFLOW_BROWSER_REAL_CLICK'); console.log('test successful');
        })().catch(e=>console.error(e));
        """,
            ready="odoo.isReady === true",
            login="admin",
            timeout=90,
        )
        record.invalidate_recordset()
        self.assertEqual(record.quantity, 7, "WORKFLOW_FORM_SERVER_VALUE")
        self.assertEqual(record.suggestion, 9)
        self.assertEqual(record.state, "confirmed")
        _logger.info("WORKFLOW_PASS browser_form")
