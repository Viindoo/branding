# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from lxml import html

from odoo.addons.viin_brand.tools import VIINDOO_SOCIAL_LINKS
from odoo.tests.common import TransactionCase, tagged

SERVER_NETWORKS = (
    "social_facebook", "social_instagram", "social_twitter", "social_linkedin", "social_tiktok",
)


@tagged("post_install", "-at_install")
class TestMailingSocialLinks(TransactionCase):
    """A mailing links to Viindoo's accounts where the company has none of its own."""

    def _rendered_links(self, company):
        block = self.env["ir.qweb"]._render("mass_mailing.s_social_media_template", {"res_company": company})
        links = html.fragment_fromstring(str(block), create_parent="div").xpath("//a[@data-platform]")
        return {link.get("data-platform").removeprefix("customLink-"): link.get("href") for link in links}

    def test_a_company_without_links_shows_the_viindoo_accounts(self):
        company = self.env["res.company"].create({"name": "No social links"})

        links = self._rendered_links(company)

        self.assertEqual(links, {network: VIINDOO_SOCIAL_LINKS[network] for network in SERVER_NETWORKS})
        for href in links.values():
            self.assertNotIn("odoo", href.lower())

    def test_a_company_link_wins_over_the_viindoo_account(self):
        company = self.env["res.company"].create({
            "name": "Own links",
            "social_facebook": "https://www.facebook.com/our.company",
        })

        links = self._rendered_links(company)

        self.assertEqual(links["social_facebook"], "https://www.facebook.com/our.company")
        self.assertEqual(links["social_linkedin"], VIINDOO_SOCIAL_LINKS["social_linkedin"])
