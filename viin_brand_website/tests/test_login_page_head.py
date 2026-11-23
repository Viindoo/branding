# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# With `website` installed the login page is rendered by website.layout: the title comes from the
# website and the favicon is the one the website is configured with, the Viindoo one while nobody
# set another.
import re

from odoo.tests.common import HttpCase, tagged
from odoo.tools import file_open

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_LINK_RE = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
_SHORTCUT_ICON_RE = re.compile(r'rel\s*=\s*["\']shortcut icon["\']', re.IGNORECASE)
_HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestLoginPageHead(HttpCase):

    def test_login_page_title_does_not_name_odoo(self):
        response = self.url_open("/web/login")

        self.assertEqual(response.status_code, 200)
        title = _TITLE_RE.search(response.text).group(1).strip()
        self.assertTrue(title)
        self.assertNotRegex(title, r"\bOdoo\b")

    def test_login_page_favicon_is_the_viindoo_one_while_the_website_keeps_its_default(self):
        website = self.env.ref("base.default_website")
        response = self.url_open("/web/login")

        self.assertEqual(response.status_code, 200)
        links = [link for link in _LINK_RE.findall(response.text) if _SHORTCUT_ICON_RE.search(link)]
        self.assertEqual(len(links), 1)
        href = _HREF_RE.search(links[0]).group(1)
        self.assertRegex(href, r"^/web/image/website/%d/favicon\?unique=" % website.id)
        favicon = self.url_open(href)
        with file_open("viin_brand/static/img/favicon.ico", "rb") as brand_favicon:
            self.assertEqual(favicon.content, brand_favicon.read())
