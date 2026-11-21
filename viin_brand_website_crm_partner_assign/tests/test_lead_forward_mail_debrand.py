# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestLeadForwardMailDebrand(TransactionCase):

    def test_lead_forward_mail_is_powered_by_viindoo(self):
        template = self.env.ref("website_crm_partner_assign.email_template_lead_forward_mail")
        body = template.with_context(lang="en_US").body_html
        self.assertNotRegex(body, BRAND_NAME)
        self.assertRegex(body, r"Powered by <a [^>]*href=\"https://viindoo\.com[^\"]*\"[^>]*>Viindoo</a>")
