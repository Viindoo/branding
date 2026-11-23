# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from lxml import etree

from odoo.tests.common import HttpCase, TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestSlidesDebrandViews(TransactionCase):

    def test_content_description_placeholder_is_a_neutral_example(self):
        view = self.env["slide.slide"].get_view(
            view_id=self.env.ref("website_slides.view_slide_slide_form").id, view_type="form",
        )
        fields = etree.fromstring(view["arch"].encode()).xpath("//field[@name='description']")
        self.assertTrue(fields)
        placeholder = fields[0].get("placeholder")
        self.assertTrue(placeholder)
        self.assertNotRegex(placeholder, BRAND_NAME)
        self.assertNotIn("Viindoo", placeholder)


@tagged("post_install", "-at_install")
class TestSlidesHomepageTitle(HttpCase):

    def test_courses_homepage_title_has_no_product_name(self):
        response = self.url_open("/slides")
        self.assertEqual(response.status_code, 200)
        title = re.search(r"<title[^>]*>(.*?)</title>", response.text, re.S | re.I).group(1)
        self.assertNotRegex(title, BRAND_NAME)
        self.assertNotIn("Viindoo", title)
        self.assertTrue(title.strip())
