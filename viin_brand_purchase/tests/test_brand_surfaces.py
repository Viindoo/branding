import re

from odoo.tests.common import TransactionCase, tagged

PRODUCT_NAME = re.compile(r'\bOdoo\b|odoo\.com', re.IGNORECASE)


@tagged('post_install', '-at_install')
class TestPurchaseBrandSurfaces(TransactionCase):

    def test_portal_connect_software_modal_does_not_promote_odoo(self):
        modal = self.env.ref('purchase.portal_my_purchase_order')._get_combined_arch().xpath(
            "//div[@id='portal_connect_software_modal']")
        self.assertEqual(len(modal), 1)
        text = ' '.join(modal[0].itertext())
        self.assertNotRegex(text, PRODUCT_NAME)
        self.assertIn('Viindoo', text)
        self.assertFalse(modal[0].xpath('.//a[contains(@href, "odoo.com")]'))
        self.assertTrue(modal[0].xpath('.//input[@readonly]'), 'the REST URL stays')

    def test_digest_tips_name_viindoo_not_a_neutral_word(self):
        for xmlid in ('purchase.digest_tip_purchase_0', 'purchase.digest_tip_purchase_1'):
            with self.subTest(tip=xmlid):
                text = self.env.ref(xmlid).with_context(lang='en_US').tip_description
                self.assertNotRegex(text, PRODUCT_NAME)
                self.assertNotRegex(text, r'\bthe system\b')
                self.assertIn('Viindoo', text)

    def test_vendor_bill_empty_state_does_not_name_odoo(self):
        help_text = self.env.ref('purchase.act_res_partner_2_supplier_invoices').with_context(lang='en_US').help
        self.assertNotRegex(help_text, PRODUCT_NAME)

    def test_portal_connect_software_modal_is_rewritten_whatever_the_language_of_its_text(self):
        self.env['res.lang']._activate_lang('ar_001')
        view = self.env.ref('purchase.portal_my_purchase_order')
        terms = {
            'Want to import this document in Odoo?': 'ar import',
            'Not using Odoo?': 'ar not using',
            "You don't use a good CRM software?": 'ar crm',
        }
        view.update_field_translations('arch_db', {'ar_001': terms})
        modal = view.with_context(lang='ar_001')._get_combined_arch().xpath("//div[@id='portal_connect_software_modal']")
        self.assertEqual(len(modal), 1)
        text = ' '.join(modal[0].itertext())
        self.assertNotRegex(text, PRODUCT_NAME)
        self.assertIn('Viindoo', text)
        self.assertNotIn('ar crm', text)
