# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestValidationMailTranslation(NoupdateTranslationCase):

    def test_validation_mail_of_a_language_loaded_before_the_module_names_viindoo(self):
        self.load_stock_then_branding_catalog(['website_profile'], 'viin_brand_website_profile')
        template = self.env.ref('website_profile.validation_email')
        self.assertHoldsStockWording(self.translated(template, 'body_html'))
        self.load_catalog('viin_brand_website_profile')
        self.assertNamesNoOdoo(self.translated(template, 'body_html'))
