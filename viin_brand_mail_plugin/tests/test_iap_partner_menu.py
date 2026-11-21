from odoo.addons.viin_brand.tests.common import HiddenMenuCase
from odoo.addons.viin_brand_mail_plugin import uninstall_hook
from odoo.tests.common import tagged


@tagged("post_install", "-at_install")
class TestIapPartnerMenu(HiddenMenuCase):

    def test_partner_enrichment_menu_is_archived_until_uninstall(self):
        menu = self.env.ref("mail_plugin.res_partner_iap_menu")
        self.assertFalse(menu.active)
        self.assertNotIn(menu.id, self.web_client_menu_ids())

        uninstall_hook(self.env)

        self.assertTrue(menu.active)
