# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestSignupMailTranslation(NoupdateTranslationCase):

    def test_signup_mails_of_a_language_loaded_before_the_module_name_viindoo(self):
        self.load_stock_then_branding_catalog(['auth_signup'], 'viin_brand_auth_signup')
        invite = self.env.ref('auth_signup.set_password_email')
        values = [(invite, 'subject'), (invite, 'body_html')] + [
            (self.env.ref(xmlid), 'body_html')
            for xmlid in (
                'auth_signup.mail_template_user_signup_account_created',
                'auth_signup.portal_set_password_email',
            )
        ]
        for record, field in values:
            self.assertHoldsStockWording(self.translated(record, field))
        self.load_catalog('viin_brand_auth_signup')
        for record, field in values:
            self.assertNamesNoOdoo(self.translated(record, field))

    def test_mail_text_a_user_wrote_survives_the_reload(self):
        self.load_stock_then_branding_catalog(['auth_signup'], 'viin_brand_auth_signup')
        template = self.env.ref('auth_signup.portal_set_password_email').with_context(lang='vi_VN')
        template.body_html = '<p>Nội dung của công ty.</p>'
        self.load_catalog('viin_brand_auth_signup')
        self.assertEqual(self.translated(template, 'body_html'), '<p>Nội dung của công ty.</p>')
