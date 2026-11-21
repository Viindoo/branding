import re

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

PRODUCT_NAME = re.compile(r'\bOdoo\b|odoo\.com', re.IGNORECASE)


@tagged('post_install', '-at_install')
class TestSaleBrandSurfaces(TransactionCase):

    def test_quotation_empty_states_link_nowhere_outside_viindoo(self):
        for xmlid in ('sale.action_quotations_with_onboarding', 'sale.action_quotations',
                      'sale.action_orders_upselling'):
            with self.subTest(action=xmlid):
                help_text = self.env.ref(xmlid).with_context(lang='en_US').help
                self.assertNotRegex(help_text, PRODUCT_NAME)
                self.assertNotRegex(help_text, r'\bthe system\b')
                self.assertNotIn('href=', help_text)

    def test_portal_connect_software_modal_does_not_promote_odoo(self):
        modal = self.env.ref('sale.sale_order_portal_template')._get_combined_arch().xpath(
            "//div[@id='sale_portal_connect_software_modal']")
        self.assertEqual(len(modal), 1)
        text = ' '.join(modal[0].itertext())
        self.assertNotRegex(text, PRODUCT_NAME)
        self.assertIn('Viindoo', text)
        self.assertFalse(modal[0].xpath('.//a[contains(@href, "odoo.com")]'))
        self.assertTrue(modal[0].xpath('.//input[@readonly]'), 'the REST URL stays')

    def test_shipping_connector_rows_are_hidden_from_sales_settings(self):
        arch = etree.fromstring(self.env['res.config.settings'].get_view(view_type='form')['arch'])
        for setting_id in ('ups', 'shipping_costs_dhl', 'shipping_costs_fedex', 'shipping_costs_usps'):
            rows = arch.xpath('//setting[@id="%s"]' % setting_id)
            self.assertEqual(len(rows), 1, setting_id)
            self.assertEqual(rows[0].get('invisible'), '1', setting_id)

    def test_portal_connect_software_modal_is_rewritten_whatever_the_language_of_its_text(self):
        self.env['res.lang']._activate_lang('ar_001')
        view = self.env.ref('sale.sale_order_portal_template')
        terms = {
            'Want to import this document in Odoo?': 'ar import',
            'Not using Odoo?': 'ar not using',
            "You don't use a good CRM software?": 'ar crm',
        }
        view.update_field_translations('arch_db', {'ar_001': terms})
        modal = view.with_context(lang='ar_001')._get_combined_arch().xpath("//div[@id='sale_portal_connect_software_modal']")
        self.assertEqual(len(modal), 1)
        text = ' '.join(modal[0].itertext())
        self.assertNotRegex(text, PRODUCT_NAME)
        self.assertIn('Viindoo', text)
        self.assertNotIn('ar crm', text)
