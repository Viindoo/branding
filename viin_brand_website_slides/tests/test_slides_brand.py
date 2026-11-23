# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import _iter_rules, _normalize_colour

FRONTEND_BUNDLE = "web.assets_frontend"
BRAND_PURPLE = "#7f4282"
ACCENT_TEXT = "#7f4282"
CYAN = "#00bbce"
ODOO_PURPLE = "#875a7b"


@tagged("post_install", "-at_install")
class TestCourseCover(TransactionCase):

    def test_the_header_of_a_new_course_has_the_viindoo_gradient(self):
        cover = self.env["slide.channel"]._default_cover_properties()

        style = cover["background_color_style"].lower()

        self.assertIn(CYAN, style)
        self.assertIn(BRAND_PURPLE, style)
        self.assertNotIn(ODOO_PURPLE, style)


@tagged("post_install", "-at_install")
class TestCoursePalette(TransactionCase):
    """The colours of the course pages follow the brand, read from the compiled frontend bundle."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        bundle = cls.env["ir.qweb"]._get_asset_bundle(FRONTEND_BUNDLE, css=True, js=False)
        cls.css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in (bundle.css() or [])
        )

    def _last(self, selector, prop):
        """The last colour the rules of ``selector`` declare for ``prop``."""
        pattern = re.compile(r"(?:^|;)\s*%s\s*:\s*([^;}]+)" % re.escape(prop))
        values = [
            _normalize_colour(match.group(1).strip())
            for _order, rule_selector, body in _iter_rules(self.css) if rule_selector == selector
            for match in pattern.finditer(body)
        ]
        return values[-1] if values else None

    def test_the_bundle_compiles(self):
        self.assertTrue(self.css.strip())
        self.assertNotIn("CSS error", self.css)

    def test_progress_bars_and_course_header_are_the_brand_purple(self):
        for selector, prop in (
            (".o_wslides_channel_completion_progressbar .progress .progress-bar", "background-color"),
            (".o_wslides_home_content_section .progress .progress-bar", "background-color"),
            (".o_wslides_course_header", "background"),
        ):
            with self.subTest(selector=selector):
                self.assertEqual(self._last(selector, prop), BRAND_PURPLE)

    def test_hovered_tabs_take_the_accent_text_colour_never_the_decorative_cyan(self):
        for selector in (
            ".o_wprofile_nav_tabs .nav-link:not(.active):hover",
            ".o_wslides_course_main .o_wslides_nav_tabs .nav-link:not(.active):hover",
        ):
            with self.subTest(selector=selector):
                colour = self._last(selector, "background")
                self.assertEqual(colour, ACCENT_TEXT)
                self.assertNotEqual(colour, CYAN)

    def _at_rule_around(self, selector):
        """The at-rule prelude of the block that holds the last rule of ``selector``, '' at top level."""
        matches = list(re.finditer(re.escape(selector) + r"\s*\{", self.css))
        self.assertTrue(matches, "no rule for %s" % selector)
        position = matches[-1].start()
        depth = 0
        for index in range(position - 1, -1, -1):
            char = self.css[index]
            if char == "}":
                depth += 1
            elif char == "{":
                if depth == 0:
                    start = max(self.css.rfind(mark, 0, index) for mark in "};{")
                    return self.css[start + 1:index].strip()
                depth -= 1
        return ""

    def test_the_tab_hover_fill_starts_where_core_sets_the_white_label_of_the_tab(self):
        """Below md the label of a tab keeps the link colour: a fill under it would hide it."""
        for selector in (
            ".o_wprofile_nav_tabs .nav-link:not(.active):hover",
            ".o_wslides_course_main .o_wslides_nav_tabs .nav-link:not(.active):hover",
        ):
            with self.subTest(selector=selector):
                self.assertIn("min-width", self._at_rule_around(selector))

    def test_the_level_up_tooltip_of_a_quiz_is_not_the_purple_of_odoo(self):
        colour = self._last(".o_wslides_quiz_modal .tooltip.bs-tooltip-top .tooltip-inner", "background-color")

        self.assertEqual(colour, BRAND_PURPLE)
