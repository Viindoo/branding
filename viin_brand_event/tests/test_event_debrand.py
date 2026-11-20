# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestEventDebrand(TransactionCase):

    def test_done_stage_description_names_viindoo(self):
        stage = self.env.ref("event.event_stage_done").with_context(lang="en_US")
        self.assertNotRegex(stage.description, BRAND_NAME)
        self.assertIn("Viindoo", stage.description)

    def test_website_placeholder_of_the_event_form_suggests_a_neutral_address(self):
        view = self.env["event.event"].get_view(
            view_id=self.env.ref("event.view_event_form").id, view_type="form",
        )
        fields = etree.fromstring(view["arch"].encode()).xpath("//field[@name='event_url']")
        self.assertEqual(len(fields), 1)
        self.assertNotRegex(fields[0].get("placeholder"), BRAND_NAME)
        self.assertEqual(fields[0].get("placeholder"), 'e.g. "https://www.example.com"')
