# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestTotpInviteTranslation(NoupdateTranslationCase):

    def test_invitation_subject_of_a_language_loaded_before_the_module_names_viindoo(self):
        self.load_stock_then_branding_catalog(['auth_totp_mail'], 'viin_brand_auth_totp_mail')
        template = self.env.ref('auth_totp_mail.mail_template_totp_invite')
        self.assertNamesNoOdoo(self.translated(template, 'subject'))
        self.load_catalog('viin_brand_auth_totp_mail')
        self.assertNamesNoOdoo(self.translated(template, 'subject'))
