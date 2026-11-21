from odoo.tests.common import TransactionCase, tagged

from .test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    CHROME_BASE,
    DARK_BUNDLE,
    DARK_LINK_REF,
    _computed_value,
    _normalize_colour,
)

# The three states core styles from the "action" entry of `$o-text-colors-custom`:
# resting action text, a link-styled action button while hovered (an activity's Edit
# link) and a pressed action toggle (the chatter Followers button of a follower).
RESTING_TEXT = {
    "tag": "span",
    "classes": frozenset({"text-action"}),
    "ancestors": frozenset({"o_web_client"}),
}
HOVERED_LINK_BUTTON = {
    "tag": "button",
    "classes": frozenset({"btn", "btn-link", "text-action"}),
    "states": frozenset({"hover"}),
    "ancestors": frozenset({"o_web_client"}),
}
PRESSED_TOGGLE = {
    "tag": "button",
    "classes": frozenset({"btn", "btn-link", "text-action", "active"}),
    "ancestors": frozenset({"o_web_client"}),
}

# The interactive teal per bundle and its pressed rung, Bootstrap's 30% link shade.
EXPECTED = {
    BACKEND_BUNDLE: {
        "resting": CHROME_BASE,
        "hovered": CHROME_BASE,
        "pressed": "#005963",
    },
    DARK_BUNDLE: {
        "resting": DARK_LINK_REF,
        "hovered": DARK_LINK_REF,
        "pressed": "#37949e",
    },
}


@tagged("post_install", "-at_install")
class TestTextActionTierCompile(TransactionCase):
    """Core's action text takes the interactive teal, not the decorative brand teal."""

    def _compiled_css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace")
            for attachment in attachments
        )
        self.assertTrue(css.strip(), "%s compiled to empty CSS" % bundle_name)
        return css

    def test_action_text_renders_the_interactive_teal_in_both_schemes(self):
        elements = {
            "resting": RESTING_TEXT,
            "hovered": HOVERED_LINK_BUTTON,
            "pressed": PRESSED_TOGGLE,
        }
        for bundle_name, expected in EXPECTED.items():
            css = self._compiled_css(bundle_name)
            for state, element in elements.items():
                with self.subTest(bundle=bundle_name, state=state):
                    value = _computed_value(css, [element], ("color",))
                    self.assertIsNotNone(
                        value, "no colour applies to %s action text" % state
                    )
                    self.assertEqual(
                        _normalize_colour(value),
                        expected[state],
                        "%s action text renders %r in %s" % (state, value, bundle_name),
                    )
