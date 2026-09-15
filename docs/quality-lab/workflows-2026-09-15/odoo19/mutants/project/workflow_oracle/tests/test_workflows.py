import logging
from pathlib import Path
import subprocess

from odoo import Command, fields
from odoo.exceptions import AccessError
from odoo.tests import tagged, new_test_user
from odoo.tests.common import TransactionCase, HttpCase
from odoo.addons.account.tests.common import AccountTestInvoicingCommon

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
    def test_historical_invoice_pdf(self):
        self.env["res.lang"]._activate_lang("fr_FR")
        self.partner_a.lang = "fr_FR"
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "invoice_date": fields.Date.from_string("2020-02-03"),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": label,
                            "quantity": 1,
                            "price_unit": price,
                            "tax_ids": [Command.clear()],
                            "account_id": self.company_data[
                                "default_account_revenue"
                            ].id,
                        }
                    )
                    for label, price in [
                        ("Prestation historique", 7),
                        ("Forfait convenu", 42),
                        ("Explication gratuite", 0),
                    ]
                ],
            }
        )
        move.action_post()
        self.assertEqual(move.state, "posted")
        self.assertEqual(move.amount_total, 49)
        invoice_user = new_test_user(
            self.env,
            login="invoice_lab",
            groups="account.group_account_invoice",
            company_id=move.company_id.id,
            company_ids=[Command.set(move.company_id.ids)],
            lang="en_US",
        )
        pdf, _ = (
            self.env["ir.actions.report"]
            .with_user(invoice_user)
            .with_context(lang="en_US", force_report_rendering=True)
            ._render_qweb_pdf("account.account_invoices", [move.id])
        )
        self.assertTrue(pdf.startswith(b"%PDF"))
        output = Path("/tmp/workflow-evidence")
        output.mkdir(exist_ok=True)
        (output / "historical-invoice.pdf").write_bytes(pdf)
        rendered = subprocess.run(
            ["pdftotext", "-", "-"], input=pdf, capture_output=True, check=True
        ).stdout.decode()
        for label in [
            "Prestation historique",
            "Forfait convenu",
            "Explication gratuite",
        ]:
            self.assertIn(label, rendered, "WORKFLOW_INVOICE_LINE")
        self.assertIn("49", rendered)
        self.assertIn("Facture", rendered, "WORKFLOW_INVOICE_LANGUAGE")
        (output / "historical-invoice.txt").write_text(rendered)
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
