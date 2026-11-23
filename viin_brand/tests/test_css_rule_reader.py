# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import BaseCase, tagged

from .test_brand_cascade_compile import _iter_rules


def _rules(css):
    """The ``(selector, declarations)`` pairs the reader yields, whitespace squeezed."""
    return [(selector, " ".join(body.split())) for _order, selector, body in _iter_rules(css)]


@tagged("post_install", "-at_install")
class CssRuleReaderTest(BaseCase):
    """The CSS reader of the cascade tests keeps what applies everywhere and drops what a parent scopes."""

    def test_flat_rules_come_out_one_selector_at_a_time_in_source_order(self):
        css = "/* a/banner.scss */ .a, .b:not(.c, .d){color: red;} .e{margin: 0;}"

        self.assertEqual(_rules(css), [
            (".a", "color: red;"), (".b:not(.c, .d)", "color: red;"), (".e", "margin: 0;"),
        ])
        self.assertEqual([order for order, _selector, _body in _iter_rules(css)], [0, 0, 1])

    def test_a_rule_nested_in_a_style_rule_is_not_a_rule_of_its_own(self):
        css = (
            ".o-sheet{color: red; .bg-white{background: var(--sheet)} &.active{margin: 1px} padding: 2px;} "
            ".bg-white{background: white;}"
        )

        self.assertEqual(_rules(css), [
            (".o-sheet", "color: red; padding: 2px;"),
            (".bg-white", "background: white;"),
        ])

    def test_a_rule_nested_deeper_is_dropped_with_its_parent(self):
        css = ".a{.b{.c{color: red;}} margin: 0;} .d{color: blue;}"

        self.assertEqual(_rules(css), [(".a", "margin: 0;"), (".d", "color: blue;")])

    def test_rules_inside_an_at_rule_wrapper_are_rules_of_their_own(self):
        css = (
            "@media (min-width: 1px){.a{color: red;} .b{.c{color: blue;}}} "
            "@supports (display: grid){.d{display: grid;}}"
        )

        self.assertEqual(_rules(css), [(".a", "color: red;"), (".b", ""), (".d", "display: grid;")])

    def test_keyframe_steps_and_font_faces_are_read_as_rules(self):
        css = "@keyframes spin{from{opacity: 0;} to{opacity: 1;}} @font-face{font-family: x;}"

        self.assertEqual(_rules(css), [
            ("from", "opacity: 0;"), ("to", "opacity: 1;"), ("@font-face", "font-family: x;"),
        ])
