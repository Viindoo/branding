from odoo.tests.common import TransactionCase, tagged

from .test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BUNDLE,
    _alpha_of,
    _normalize_colour,
    _winning_declaration,
)

# `$o-gray-700` of each bundle: core's light ramp, and viin_brand's dark ramp
# (mix($body-secondary-color, $body-emphasis-color) in dark_palette.scss).
INACTIVE_STEP_TEXT = {
    BACKEND_BUNDLE: "#495057",
    DARK_BUNDLE: "#acbec0",
}

# A read-only statusbar step that is not the current one, as core renders it in a form.
INACTIVE_STEP = {
    "tag": "button",
    "classes": frozenset(
        {"btn", "btn-secondary", "o_arrow_button", "o_viin_numbered_step"}
    ),
    "states": frozenset({"disabled"}),
    "parent": frozenset({"o_statusbar_status"}),
    "ancestors": frozenset(
        {
            "o_web_client",
            "o_form_view",
            "o_field_widget",
            "o_field_statusbar",
            "o_statusbar_status",
        }
    ),
}


@tagged("post_install", "-at_install")
class TestStatusbarStepsCompile(TransactionCase):
    """Inactive numbered statusbar steps print their label in the opaque ramp grey."""

    def _compiled_css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace")
            for attachment in attachments
        )
        self.assertTrue(css.strip(), "%s compiled to empty CSS" % bundle_name)
        return css

    def test_inactive_step_label_is_the_opaque_ramp_grey_in_both_schemes(self):
        for bundle_name, expected in INACTIVE_STEP_TEXT.items():
            css = self._compiled_css(bundle_name)
            for state in ("disabled", "hover"):
                with self.subTest(bundle=bundle_name, state=state):
                    element = dict(INACTIVE_STEP, states=frozenset({"disabled", state}))
                    value = _winning_declaration(css, element, ("color",))
                    self.assertIsNotNone(value, "no colour applies to an inactive step")
                    self.assertEqual(
                        (_normalize_colour(value), _alpha_of(value)),
                        (expected, 1.0),
                        "an inactive step label renders %r in %s"
                        % (value, bundle_name),
                    )
