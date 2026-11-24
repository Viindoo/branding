# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Compiled-CSS guards for the Discuss sidebar type scale, the white ring of the call buttons and the
# absence of a ring on the unread counters. Rules are read from the compiled bundles the way a browser
# resolves them: the last matching declaration wins.
import re

from odoo.tests.common import TransactionCase, tagged

from .test_mail_contrast_compile import (
    ANY_ANCESTORS,
    BACKEND_BUNDLE,
    DARK_BUNDLE,
    ContrastCompileHelpers,
    _bodies_matching,
    _declared_values,
)

ROOT_FONT_SIZE_PX = 16.0

# selector -> font size in px (core size * 1.125)
SIDEBAR_FONT_SIZES = {
    ".o-mail-DiscussSidebarChannel-itemName": 15.75,
    ".o-mail-DiscussSidebarChannel-floatingName": 15.75,
    ".o-mail-DiscussSearch-inputContainer input": 15.75,
    ".o-mail-Mailbox .small": 14.625,
    ".o-mail-DiscussSidebarCategory-title": 13.5,
    ".o-mail-DiscussSidebarChannel-subChannel": 13.5,
    ".o-mail-DiscussSidebar-badge": 12.375,
    ".o-mail-DiscussSidebar-badge .o-innerBadge": 12.375,
    ".o-mail-DiscussSidebarCategory-icon": 11.7,
    ".o-mail-DiscussSidebarCategory-chevronCompact": 11.7,
}

_FONT_SIZE_RE = re.compile(r"(?<![\w-])font-size\s*:\s*([^;]+)", re.IGNORECASE)
_BORDER_RE = re.compile(r"(?<![\w-])border\s*:\s*([^;]+)", re.IGNORECASE)

# selector of the element carrying the ring, as compiled
RINGED_SELECTORS = (".o-mail-ChatWindow-header .o-tag-JOIN_LEAVE_CALL > i",)
# unread counters: the purple fill separates them from the chrome, they carry no ring
UNRINGED_COUNTER_SELECTORS = (
    ".o_main_navbar .o_menu_systray .o-mail-MessagingMenu-counter",
    ".o_main_navbar .o_menu_systray .o-mail-ActivityMenu-counter",
    ".o-mail-ChatWindow-header .o-mail-ChatWindow-counter",
    ".o-mail-MessagingMenu-counter",
    ".o-mail-ActivityMenu-counter",
    ".o-mail-ChatWindow-counter",
)


def _to_px(value):
    match = re.fullmatch(r"([0-9.]+)(rem|px)", value.strip())
    if not match:
        return None
    number = float(match.group(1))
    return number * ROOT_FONT_SIZE_PX if match.group(2) == "rem" else number


def _last_declared_in(test, css, selector, pattern):
    """Return the value the last compiled rule of ``selector`` declares for ``pattern``."""
    bodies = _bodies_matching(css, lambda token: token == selector, ANY_ANCESTORS)
    values = _declared_values(bodies, pattern)
    test.assertTrue(values, "no compiled rule of %r declares the property" % selector)
    return values[-1]


@tagged("post_install", "-at_install")
class TestDiscussChromeCompile(ContrastCompileHelpers, TransactionCase):

    def _last_declared(self, css, selector, pattern):
        return _last_declared_in(self, css, selector, pattern)

    def test_discuss_sidebar_type_is_one_eighth_larger_in_both_schemes(self):
        for bundle in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._compiled_css(bundle)
            for selector, expected in SIDEBAR_FONT_SIZES.items():
                with self.subTest(bundle=bundle, selector=selector):
                    size = _to_px(self._last_declared(css, selector, _FONT_SIZE_RE))
                    self.assertIsNotNone(size, "%s font-size is not a rem or px length" % selector)
                    self.assertAlmostEqual(size, expected, places=2)

    def test_discuss_sidebar_scale_leaves_message_content_alone(self):
        css = self._compiled_css(BACKEND_BUNDLE)
        for selector in (".o-mail-Message-content", ".o-mail-Composer-input", ".o-mail-Message-author"):
            with self.subTest(selector=selector):
                bodies = _bodies_matching(css, lambda token: token == selector, ANY_ANCESTORS)
                scaled = [
                    value for value in _declared_values(bodies, _FONT_SIZE_RE)
                    if _to_px(value) in (15.75, 14.625, 13.5, 12.375)
                ]
                self.assertEqual(scaled, [])

    def test_the_call_buttons_on_the_teal_chrome_carry_a_white_ring_in_both_schemes(self):
        for bundle in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._compiled_css(bundle)
            for selector in RINGED_SELECTORS:
                with self.subTest(bundle=bundle, selector=selector):
                    border = self._last_declared(css, selector, _BORDER_RE)
                    self.assertIn(
                        border,
                        ("1px solid #fff", "1px solid #ffffff", "1px solid white"),
                        "%s must carry a 1px white ring on all four sides" % selector,
                    )

    def test_the_unread_counters_carry_no_ring_in_both_schemes(self):
        for bundle in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._compiled_css(bundle)
            for selector in UNRINGED_COUNTER_SELECTORS:
                with self.subTest(bundle=bundle, selector=selector):
                    bodies = _bodies_matching(css, lambda token: token == selector, ANY_ANCESTORS)
                    borders = [
                        value for value in _declared_values(bodies, _BORDER_RE)
                        if value.strip() not in ("0", "none")
                    ]
                    self.assertEqual(
                        borders, [],
                        "%s must not draw a ring: the purple fill already separates it" % selector,
                    )
