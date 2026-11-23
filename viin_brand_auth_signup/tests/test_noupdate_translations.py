# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestSignupMailTranslation(NoupdateTranslationCase):

    def test_invitation_of_a_language_loaded_before_the_module_names_viindoo(self):
        self.load_stock_then_branding_catalog(['auth_signup'], 'viin_brand_auth_signup')
        invite = self.env.ref('auth_signup.set_password_email')
        self.assertNamesNoOdoo(self.translated(invite, 'subject'))
        self.load_catalog('viin_brand_auth_signup')
        self.assertNamesNoOdoo(self.translated(invite, 'subject'))
        self.assertNamesNoOdoo(self.translated(invite, 'body_html'))
