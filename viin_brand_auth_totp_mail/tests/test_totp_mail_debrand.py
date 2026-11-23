# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re
from urllib.parse import urlsplit

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestTotpMailDebrand(TransactionCase):

    def test_security_alert_links_the_two_factor_guide_of_viindoo(self):
        arch = self.env.ref("mail.account_security_alert")._get_combined_arch()
        hrefs = arch.xpath("//div[@t-if='suggest_2fa']/a/@href")
        self.assertEqual(len(hrefs), 1)
        self.assertNotRegex(hrefs[0], BRAND_NAME)
        self.assertEqual(urlsplit(hrefs[0]).hostname, "viindoo.com")

    def test_invitation_subject_names_viindoo(self):
        subject = self.env.ref("auth_totp_mail.mail_template_totp_invite").with_context(lang="en_US").subject
        self.assertNotRegex(subject, BRAND_NAME)
        self.assertIn("Viindoo", subject)

    def test_email_code_login_form_names_no_odoo(self):
        arch = self.env.ref("auth_totp_mail.auth_totp_mail_form")._get_combined_arch()
        shown = " ".join(arch.xpath("//text()")) + " ".join(arch.xpath("//@href"))
        self.assertNotRegex(shown, BRAND_NAME)
