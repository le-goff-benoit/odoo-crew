import logging

from odoo.tests import tagged
from odoo.tests.common import HttpCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestBrowserConfirmation(HttpCase):
    def test_browser_confirmation(self):
        record = self.env["lab.qualification"].create({"name": "Browser witness", "quantity": 3})
        action = self.env.ref("lab_qualification.quantity_action")
        self.assertEqual(record.state, "draft")
        self.browser_js(
            f"/odoo/action-{action.id}/{record.id}",
            """
            (async () => {
                const wait = async (predicate) => {
                    for (let index = 0; index < 150; index++) {
                        const value = predicate();
                        if (value) return value;
                        await new Promise(resolve => setTimeout(resolve, 100));
                    }
                    throw new Error('Expected real form state not reached');
                };
                const button = await wait(() => document.querySelector('button[name="action_confirm"]'));
                if (!document.body.textContent.includes('Browser witness')) {
                    throw new Error('Wrong record displayed');
                }
                button.click();
                await wait(() => document.querySelector('.o_statusbar_status button[data-value="confirmed"].o_arrow_button_current'));
                console.log('QUALIFICATION_BROWSER_CLICK_OK');
                console.log('test successful');
            })().catch(error => console.error(error));
            """,
            ready="odoo.isReady === true",
            login="admin",
            timeout=90,
        )
        record.invalidate_recordset()
        self.assertEqual(record.state, "draft", "QUALIFICATION_SERVER_STATE")
        self.assertEqual(record.amount, 30)
        _logger.info("QUALIFICATION_PASS browser_server")
