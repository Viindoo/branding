# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestValidationEmailDebrand(TransactionCase):

    def test_forum_validation_email_is_powered_by_viindoo(self):
        template = self.env.ref("website_profile.validation_email").with_context(lang="en_US")
        self.assertNotRegex(template.body_html, BRAND_NAME)
        self.assertRegex(template.body_html, r"Powered by <a [^>]*href=\"https://viindoo\.com[^\"]*\"[^>]*>Viindoo</a>")
