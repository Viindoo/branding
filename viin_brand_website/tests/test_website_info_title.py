# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from odoo.tests.common import HttpCase, tagged

VIINDOO_INFO_TITLE_MARKER = "Viindoo Information"
ODOO_BRAND_NAME = "Odoo"


@tagged("post_install", "-at_install")
class WebsiteInfoPageTitleTest(HttpCase):
    """Protect that the Website Info page's browser-tab <title> is de-branded, not just its body."""

    def _html_title(self, html):
        match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None

    def test_website_info_page_title_is_viindoo_not_odoo(self):
        """GET /website/info: the <title> shows Viindoo, never the core 'Odoo Information'.

        Core resolves the title from the name of the outer ``website.website_info`` view, not
        from the content template the body is branded through. The route is public, so the
        request is anonymous."""
        response = self.url_open("/website/info")
        self.assertEqual(
            response.status_code, 200,
            "Website Info page must render",
        )
        title = self._html_title(response.text)
        self.assertIsNotNone(title, "Website Info page must render a <title> element")
        self.assertIn(
            VIINDOO_INFO_TITLE_MARKER, title,
            "Website Info page <title> must be de-branded to '%s' (got %r)"
            % (VIINDOO_INFO_TITLE_MARKER, title),
        )
        self.assertNotIn(
            ODOO_BRAND_NAME, title,
            "Website Info page <title> must not leak the '%s' wordmark (got %r)"
            % (ODOO_BRAND_NAME, title),
        )
