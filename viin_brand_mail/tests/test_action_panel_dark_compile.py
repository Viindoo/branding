# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# WHAT IS PROTECTED (behaviour, not code): the radios and checkboxes of a Discuss action panel
# (notification settings, member list, ...) are not white boxes on the dark panel. Core mail fills
# them with a literal `$white` (`--form-check-bg`), which stays a real white in the dark bundle, so
# the dark bundle re-points that custom property to a dark-safe fill while the light bundle keeps
# core's white.
import re

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand_web.tests.test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BUNDLE,
    _declarations,
    _iter_rules,
    _normalize_colour,
    _relative_luminance,
)

ACTION_PANEL_CHECK = ".o-mail-ActionPanel .form-check-input"
# Relative luminance above which a surface reads as a light band on a dark page.
LIGHT_SURFACE_LUMINANCE = 0.45


@tagged("post_install", "-at_install")
class TestActionPanelDarkCompile(TransactionCase):
    def _form_check_fill(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join((a.raw or b"").decode("utf-8", "replace") for a in attachments)
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        fill = None
        for _order, selector, body in _iter_rules(css):
            if " ".join(selector.split()) == ACTION_PANEL_CHECK:
                for value, _important in _declarations(body, ("--form-check-bg",)):
                    fill = value
        return fill

    def test_dark_action_panel_form_check_is_not_a_white_box_and_light_keeps_white(self):
        dark = self._form_check_fill(DARK_BUNDLE)
        self.assertIsNotNone(dark, "the dark bundle declares no --form-check-bg for the panel")
        colour = _normalize_colour(dark)
        self.assertTrue(
            colour is None or _relative_luminance(colour) <= LIGHT_SURFACE_LUMINANCE,
            "the panel form check is the light surface %s in the dark bundle" % dark,
        )
        self.assertEqual(_normalize_colour(self._form_check_fill(BACKEND_BUNDLE) or ""), "#ffffff")
