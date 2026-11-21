# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestWebsiteEventDebrand(TransactionCase):

    def test_speaker_bio_snippet_is_a_neutral_sample_bio(self):
        arch = self.env.ref("website_event.s_speaker_bio")._get_combined_arch()
        text = " ".join(etree.tostring(arch, method="text", encoding="unicode").split())
        self.assertNotRegex(text, BRAND_NAME)
        for software_history in ("Viindoo", "TinyERP", "OpenERP"):
            self.assertNotIn(software_history, text)
        self.assertIn("John DOE has spent more than twenty years", text)
