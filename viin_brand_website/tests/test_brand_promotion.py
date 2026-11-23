# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from urllib.parse import urlparse

from lxml import html

from odoo.tests.common import HttpCase, tagged

BRAND_HOSTS = {"viindoo.com", "www.viindoo.com"}


@tagged("post_install", "-at_install")
class TestWebsiteFooterPromotion(HttpCase):
    """The promotion of every public page offers the Viindoo page, not the one of Odoo."""

    def test_footer_of_a_public_page_invites_to_create_a_viindoo_website(self):
        response = self.url_open("/")

        self.assertEqual(response.status_code, 200)
        promotion = html.fromstring(response.content).xpath("//*[hasclass('o_brand_promotion')]")
        self.assertEqual(len(promotion), 1, "the page must carry its promotion once")
        links = promotion[0].xpath(".//a")
        self.assertEqual(len(links), 2, "the Powered by link and the invitation")
        for link in links:
            self.assertIn(urlparse(link.get("href")).netloc, BRAND_HOSTS, link.get("href"))
        invitation = links[-1]
        self.assertTrue(urlparse(invitation.get("href")).path.startswith("/intro/"))
        self.assertIn("utm_medium=website", invitation.get("href"))
