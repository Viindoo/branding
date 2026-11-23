import re

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    _contrast_ratio,
    _declarations,
    _iter_rules,
    _normalize_colour,
)

FRONTEND_BUNDLE = "web.assets_frontend"


# The cascade below resolves one element only - a button carrying the classes 'btn',
# 'btn-fill-primary' and 'btn-primary' - so every candidate selector is a single bare class, specificity
# is constant across the candidates and the winner is decided by importance, then source order,
# then declaration order.
def _winning_declaration_for_button(css, prop_names):
    """Cascade winner of prop_names among rules whose selector is exactly '.btn',
    '.btn-fill-primary' or '.btn-primary', ordered by (importance, source order, declaration
    order)."""
    best_key, best_value = None, None
    for order, selector, body in _iter_rules(css):
        if selector not in (".btn", ".btn-fill-primary", ".btn-primary"):
            continue
        for decl_order, (value, important) in enumerate(_declarations(body, prop_names)):
            key = (important, order, decl_order)
            if best_key is None or key > best_key:
                best_key, best_value = key, value
    return best_value


def _resolve_button_colour(css, prop_name):
    """Resolve prop_name's winning colour on the button, following ``var(--x)`` references into the
    button classes' own custom-property declarations."""
    value = _winning_declaration_for_button(css, (prop_name,))
    depth = 6
    while value is not None and depth > 0:
        var_match = re.match(r"^var\(\s*(--[\w-]+)\s*(?:,\s*(.*))?\)$", value.strip(), re.DOTALL)
        if not var_match:
            break
        name, fallback = var_match.group(1), var_match.group(2)
        resolved = _winning_declaration_for_button(css, (name,))
        value = resolved if resolved is not None else fallback
        depth -= 1
    return _normalize_colour(value) if value else None


@tagged("post_install", "-at_install")
class HtmlEditorPrimaryButtonTest(TransactionCase):

    def _frontend_css(self):
        bundle = self.env["ir.qweb"]._get_asset_bundle(FRONTEND_BUNDLE, css=True, js=False)
        attachments = bundle.css()
        css_text = attachments[0].raw.decode() if attachments else ""
        self.assertTrue(css_text)
        return css_text

    def test_primary_button_text_is_readable_on_its_background(self):
        css_text = self._frontend_css()

        text_colour = _resolve_button_colour(css_text, "color")
        background_colour = _resolve_button_colour(css_text, "background-color")
        self.assertIsNotNone(text_colour)
        self.assertIsNotNone(background_colour)

        ratio = _contrast_ratio(text_colour, background_colour)
        self.assertGreaterEqual(
            ratio, 4.5,
            "primary button text %s on %s clears only %.2f:1 (WCAG AA needs 4.5:1)"
            % (text_colour, background_colour, ratio),
        )

    def test_the_editor_stylesheet_forces_a_white_primary_button_label(self):
        """The stylesheet of the module is loaded: the primary button label is white by importance.

        The contrast test above holds without that rule on the stock palette, so it cannot tell
        whether the stylesheet reaches the bundle."""
        forced_white = [
            (order, selector)
            for order, selector, body in _iter_rules(self._frontend_css())
            if selector in (".btn-fill-primary", ".btn-primary")
            for value, important in _declarations(body, ("color",))
            if important and _normalize_colour(value) == "#ffffff"
        ]

        self.assertTrue(forced_white, "no important white colour on .btn-primary in %s" % FRONTEND_BUNDLE)
