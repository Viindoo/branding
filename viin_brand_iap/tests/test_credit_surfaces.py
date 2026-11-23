from lxml import etree

from odoo.addons.viin_brand.tests.common import HiddenMenuCase
from odoo.addons.viin_brand_iap import uninstall_hook
from odoo.tests.common import tagged


@tagged('post_install', '-at_install')
class TestCreditSurfaces(HiddenMenuCase):

    def test_the_iap_block_of_general_settings_is_hidden(self):
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        nodes = etree.fromstring(arch).xpath('//setting[@id="iap_credits_setting"]')
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].get('invisible'), '1')

    def test_the_iap_block_of_general_settings_does_not_carry_the_product_name_in_its_title(self):
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        setting = etree.fromstring(arch).xpath('//setting[@id="iap_credits_setting"]')[0]
        self.assertTrue(setting.get('string'))
        self.assertNotIn('Odoo', setting.get('string'))

    def test_the_iap_menu_and_accounts_under_it_are_hidden_until_uninstall(self):
        root = self.env.ref('iap.iap_root_menu')
        accounts = self.env.ref('iap.iap_account_menu')
        self.assertFalse(root.active)
        self.assertFalse({root.id, accounts.id} & self.web_client_menu_ids())

        uninstall_hook(self.env)

        self.assertTrue(root.active)
        self.assertLessEqual({root.id, accounts.id}, self.web_client_menu_ids())

    def test_an_account_form_offers_no_way_to_buy_credits(self):
        arch = self.env['iap.account'].get_view(view_type='form')['arch']
        buttons = etree.fromstring(arch).xpath('//button[@name="action_buy_credits"]')
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].get('invisible'), '1')
