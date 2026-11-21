# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BUNDLE,
    _declarations,
    _iter_rules,
    _normalize_colour,
    _relative_luminance,
)


@tagged("post_install", "-at_install")
class TestActionPanelDarkCompile(TransactionCase):
    """Radios and checkboxes of a Discuss action panel are not white boxes on the dark panel.

    Core mail fills them with a literal white (``--form-check-bg``), so the dark bundle sets a
    dark-safe fill for it while the light bundle keeps core's white.
    """

    def _form_check_fill(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join((a.raw or b"").decode("utf-8", "replace") for a in attachments)
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        fill = None
        for _order, selector, body in _iter_rules(css):
            if " ".join(selector.split()) == ".o-mail-ActionPanel .form-check-input":
                for value, _important in _declarations(body, ("--form-check-bg",)):
                    fill = value
        return fill

    def test_dark_action_panel_form_check_is_not_a_white_box_and_light_keeps_white(self):
        dark = self._form_check_fill(DARK_BUNDLE)
        self.assertIsNotNone(dark, "the dark bundle declares no --form-check-bg for the panel")
        colour = _normalize_colour(dark)
        self.assertTrue(
            # a luminance above 0.45 reads as a light band on a dark page
            colour is None or _relative_luminance(colour) <= 0.45,
            "the panel form check is the light surface %s in the dark bundle" % dark,
        )
        self.assertEqual(_normalize_colour(self._form_check_fill(BACKEND_BUNDLE) or ""), "#ffffff")
