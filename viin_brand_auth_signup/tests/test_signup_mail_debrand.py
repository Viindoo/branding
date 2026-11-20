# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestSignupMailDebrand(TransactionCase):

    def test_signup_mail_templates_name_no_odoo_and_link_no_odoo_page(self):
        for xmlid in (
            "auth_signup.set_password_email",
            "auth_signup.mail_template_user_signup_account_created",
            "auth_signup.mail_template_data_unregistered_users",
            "auth_signup.portal_set_password_email",
        ):
            template = self.env.ref(xmlid).with_context(lang="en_US")
            self.assertNotRegex(template.subject or "", BRAND_NAME, xmlid)
            self.assertNotRegex(template.body_html or "", BRAND_NAME, xmlid)

    def test_password_reset_mail_layout_is_powered_by_viindoo(self):
        arch = self.env.ref("auth_signup.reset_password_email")._get_combined_arch()
        text = " ".join(arch.xpath("//text()")) + " ".join(arch.xpath("//@href"))
        self.assertNotRegex(text, BRAND_NAME)
