# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from odoo.tests.common import HttpCase, TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestApiDocPage(HttpCase):

    def test_documentation_page_tab_is_titled_viindoo(self):
        self.authenticate("admin", "admin")

        response = self.url_open("/doc")

        self.assertEqual(response.status_code, 200)
        title = re.search(r"<title[^>]*>(.*?)</title>", response.text, re.S | re.I).group(1)
        self.assertNotRegex(title, BRAND_NAME)
        self.assertIn("Viindoo Runtime Doc", title)


@tagged("post_install", "-at_install")
class TestApiDocBundle(TransactionCase):

    def test_documentation_client_header_is_titled_viindoo(self):
        bundle = self.env["ir.qweb"]._get_asset_bundle("api_doc.assets", css=False, js=True)
        content = (bundle.js().raw or b"").decode("utf-8", "replace")

        self.assertNotIn("in file 'viin_brand_api_doc/static/src/doc_client.xml'", content)
        self.assertIn("Viindoo Runtime Doc", content)
