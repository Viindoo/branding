# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from lxml import html

from odoo.tests.common import HttpCase, new_test_user, tagged

ODOO_DOCUMENTATION = re.compile(r"odoo\.com/documentation", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestTotpPortalDebrand(HttpCase):

    def test_portal_security_page_links_no_odoo_documentation(self):
        for login, group in (("totp_portal_customer", "base.group_portal"),
                             ("totp_portal_employee", "base.group_user")):
            with self.subTest(user=login):
                new_test_user(self.env, login=login, groups=group)
                self.authenticate(login, login)

                response = self.url_open("/my/security")

                self.assertEqual(response.status_code, 200)
                self.assertNotRegex(response.text, ODOO_DOCUMENTATION)
                links = html.fromstring(response.content).xpath(
                    "//a[contains(@href, 'two-factor-authentication')]/@href")
                self.assertEqual(len(links), 1)
                self.assertEqual(links[0], links[0].strip(), "the documentation link carries no whitespace")
                self.assertIn("viindoo.com/documentation", links[0])
