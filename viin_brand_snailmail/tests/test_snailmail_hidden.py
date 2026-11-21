from odoo.addons.viin_brand.tests.common import HiddenMenuCase
from odoo.addons.viin_brand_snailmail import uninstall_hook
from odoo.tests.common import tagged


@tagged('post_install', '-at_install')
class TestSnailmailHidden(HiddenMenuCase):

    def test_the_letters_menu_is_archived_until_uninstall(self):
        menu = self.env.ref('snailmail.menu_snailmail_letters')
        self.assertFalse(menu.active)
        self.assertNotIn(menu.id, self.web_client_menu_ids())

        uninstall_hook(self.env)

        self.assertTrue(menu.active)
        self.assertIn(menu.id, self.web_client_menu_ids())

    def test_the_letters_queue_is_not_processed(self):
        cron = self.env.ref('snailmail.snailmail_print').with_context(active_test=False)
        self.assertFalse(cron.active)
