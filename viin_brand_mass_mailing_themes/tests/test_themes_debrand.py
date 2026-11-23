# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re
from urllib.parse import urlparse

from lxml import html

from odoo.tests.common import HttpCase, tagged

SOCIAL_HOSTS = (
    "facebook.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "tiktok.com",
)
SOCIAL_THEMES = {
    "event",
    "blogging",
    "coupon",
    "magazine",
    "bignews",
    "promotion",
    "coffeebreak",
    "training",
    "catalog",
    "terms_update",
    "event_updates",
    "newsletter",
}
ODOO_MARK = re.compile(r"odoo", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestMailingThemesDebrand(HttpCase):
    """The themes offered by the mailing designer carry no Odoo mark and
    take their social links from the company.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_links = {
            "social_facebook": "https://facebook.com/company-brand",
            "social_linkedin": "https://linkedin.com/company/company-brand",
            "social_twitter": "https://twitter.com/company-brand",
            "social_instagram": "https://instagram.com/company-brand",
            "social_tiktok": "https://tiktok.com/@company-brand",
        }
        cls.env.company.write(cls.company_links)
        themes = html.fromstring(
            cls.env["ir.ui.view"].render_public_asset("mass_mailing.email_designer_themes"),
        )
        cls.themes = {
            theme.get("data-name"): theme for theme in themes.xpath("//div[@data-name][@title]")
        }

    @staticmethod
    def _social_hrefs(theme):
        hrefs = []
        for href in theme.xpath(".//a/@href"):
            host = urlparse(href).hostname or ""
            if any(host == h or host.endswith("." + h) for h in SOCIAL_HOSTS):
                hrefs.append(href)
        return hrefs

    def test_no_theme_carries_an_odoo_mark(self):
        self.assertTrue(self.themes, "The designer must offer themes")
        for name, theme in self.themes.items():
            marks = ODOO_MARK.findall(html.tostring(theme, encoding="unicode"))
            self.assertFalse(marks, "Theme %s must not carry an Odoo mark" % name)

    def test_theme_social_links_are_the_company_links(self):
        with_links = {
            name: hrefs
            for name, theme in self.themes.items()
            if (hrefs := self._social_hrefs(theme))
        }
        self.assertLessEqual(
            SOCIAL_THEMES, set(with_links), "These themes must show social links"
        )
        for name, hrefs in with_links.items():
            self.assertTrue(
                set(hrefs) <= set(self.company_links.values()),
                "Theme %s must link the company accounts, got %s" % (name, hrefs),
            )

    def test_event_theme_headline_names_viindoo(self):
        headline = self.themes["event"].xpath(".//h1")[0].text_content()
        self.assertIn("Viindoo", headline)

    def test_theme_images_of_the_module_are_served(self):
        own_urls = set()
        for theme in self.themes.values():
            own_urls.update(
                src
                for src in theme.xpath(".//img/@src")
                if src.startswith("/viin_brand_mass_mailing_themes/")
            )
        for name in ("event", "newsletter"):
            stem = self.themes[name].get("data-img")
            self.assertTrue(
                stem.startswith("/viin_brand_mass_mailing_themes/"),
                "The %s thumbnail must be the Viindoo one" % name,
            )
            # The theme picker appends these suffixes to the thumbnail stem.
            own_urls.update(stem + suffix for suffix in ("_small.webp", "_large.webp"))
        self.assertGreaterEqual(len(own_urls), 8)
        for url in sorted(own_urls):
            response = self.url_open(url)
            self.assertEqual(response.status_code, 200, "%s must be served" % url)
