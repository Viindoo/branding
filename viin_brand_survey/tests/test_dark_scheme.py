# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    DARK_BUNDLE,
    DARK_READABLE_TEXT,
    WCAG_AA_NORMAL_TEXT,
    _contrast_ratio,
    _normalize_colour,
)
from odoo.addons.viin_brand.tests.test_dark_gray_ramp_compile import _last_value

DARK_BORDER_RUNG = "#25383c"


@tagged("post_install", "-at_install")
class TestSurveyDarkScheme(TransactionCase):

    def _colour(self, css, selector, prop, label):
        value = _last_value(css, selector, prop)
        self.assertIsNotNone(value, "no %s declared on %s (%s)" % (prop, selector, label))
        colour = _normalize_colour(value)
        self.assertIsNotNone(colour, "%s on %s is not a colour: %r" % (prop, selector, value))
        return colour

    def test_survey_section_row_and_sample_card_hover_are_the_dark_border_rung(self):
        """A survey section row paints #25383C under its #EDF4F5 label (11.03:1) and the empty-state
        sample card hovers to the same #25383C with a readable label."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(DARK_BUNDLE, css=True, js=False)
        css = "".join((attachment.raw or b"").decode("utf-8", "replace") for attachment in (bundle.css() or []))
        section = self._colour(css, ".o_survey_form", "--SurveyForm__section-background-color", "section row")
        self.assertEqual(section, DARK_BORDER_RUNG)
        self.assertGreaterEqual(_contrast_ratio(DARK_READABLE_TEXT, section), 11.0)
        hover = self._colour(css, ".o_survey_sample_card", "--SurveySampleCard-background--hover", "sample card")
        self.assertEqual(hover, DARK_BORDER_RUNG)
        self.assertGreaterEqual(_contrast_ratio(DARK_READABLE_TEXT, hover), WCAG_AA_NORMAL_TEXT)
