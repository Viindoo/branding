# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re
from urllib.parse import urlparse

from lxml import etree

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open

ODOO_MARK = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)
LANG = "vi_VN"


@tagged("post_install", "-at_install")
class TestPortalSidebarPromotion(TransactionCase):
    """The "Powered by" line under the sidebar of a portal record offers the Viindoo page."""

    def _sidebar(self, lang):
        rendered = self.env["ir.qweb"].with_context(lang=lang)._render(
            "portal.portal_record_sidebar", {"classes": "", "title": "Record", "entries": ""},
        )
        return etree.HTML(str(rendered))

    def test_the_powered_by_link_and_logo_are_those_of_viindoo(self):
        sidebar = self._sidebar("en_US")

        links = sidebar.xpath("//a[img]")
        self.assertEqual(len(links), 1)
        self.assertEqual(urlparse(links[0].get("href")).netloc, "www.viindoo.com")
        self.assertEqual(links[0].get("title"), "Viindoo")
        logo = links[0].find("img")
        self.assertNotRegex(logo.get("alt"), ODOO_MARK)
        with file_open(logo.get("src").lstrip("/"), "rb") as image:
            self.assertEqual(image.read(8), b"\x89PNG\r\n\x1a\n", "the logo is served by the addons path")

    def test_the_logo_is_named_in_the_language_of_the_visitor(self):
        self.env["res.lang"]._activate_lang(LANG)
        self.env["ir.module.module"]._load_module_terms(["viin_brand_portal"], [LANG], overwrite=True)

        logo = self._sidebar(LANG).xpath("//a/img")[0]

        self.assertNotRegex(logo.get("alt"), ODOO_MARK)
        source = self._sidebar("en_US").xpath("//a/img")[0].get("alt")
        self.assertNotEqual(logo.get("alt"), source, "the alternative text is translated")


@tagged("post_install", "-at_install")
class TestPortalShareInvitation(TransactionCase):
    """The button of the invitation to a document takes the colour of the company."""

    def _button_style(self, company, lang):
        partner = self.env["res.partner"].create({"name": "Guest", "lang": lang})
        record = self.env["res.partner"].create({"name": "Shared record"})
        body = self.env["ir.qweb"].with_context(lang=lang)._render("portal.portal_share_template", {
            "partner": partner, "user": self.env.user, "company": company, "record": record,
            "model_description": "contact", "share_link": "https://example.com/share", "note": False,
        })
        button = etree.HTML(str(body)).xpath("//a[@href='https://example.com/share']")[0]
        return button.get("style")

    def test_the_button_takes_the_secondary_colour_of_the_company_in_every_language(self):
        self.env["res.lang"]._activate_lang(LANG)
        self.env["res.lang"]._activate_lang("fr_FR")
        company = self.env.company
        company.email_secondary_color = "#123456"
        for lang in ("en_US", LANG, "fr_FR"):
            with self.subTest(lang=lang):
                style = self._button_style(company, lang)
                self.assertIn("background-color: #123456", style)
                self.assertNotIn("875a7b", style.lower())

    def test_the_button_is_viindoo_purple_when_the_company_has_no_colour(self):
        company = self.env.company
        company.email_secondary_color = False

        style = self._button_style(company, "en_US")

        self.assertIn("background-color: #7F4282", style)
        self.assertNotIn("875a7b", style.lower())
