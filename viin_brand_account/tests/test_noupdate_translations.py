# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestEinvoiceMailTranslation(NoupdateTranslationCase):

    def test_einvoice_mails_of_a_language_loaded_before_the_module_name_viindoo(self):
        self.load_stock_then_branding_catalog(['account'], 'viin_brand_account')
        templates = [
            self.env.ref('account.mail_template_einvoice_notification'),
            self.env.ref('account.mail_template_invoice_subscriber'),
        ]
        for template in templates:
            self.assertHoldsStockWording(self.translated(template, 'body_html'))
        self.load_catalog('viin_brand_account')
        for template in templates:
            self.assertNamesNoOdoo(self.translated(template, 'body_html'))
