# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Compiled-CSS guards for the white ring that separates a semantic fill from the teal chrome.
# Rules are read from the compiled bundles the way a browser resolves them: the last matching
# declaration wins.
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

_BORDER_RE = re.compile(r"(?<![\w-])border\s*:\s*([^;]+)", re.IGNORECASE)
_OPACITY_RE = re.compile(r"(?<![\w-])opacity\s*:\s*([^;]+)", re.IGNORECASE)

# selector of the element carrying the ring, as compiled: a call glyph, which is not a counter
CHROME_FILL_SELECTORS = (
    ".o-mail-ChatWindow-header .o-tag-JOIN_LEAVE_CALL > i",
)


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

    def test_a_semantic_fill_on_the_teal_chrome_carries_a_white_ring_in_both_schemes(self):
        for bundle in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._compiled_css(bundle)
            for selector in CHROME_FILL_SELECTORS:
                with self.subTest(bundle=bundle, selector=selector):
                    border = self._last_declared(css, selector, _BORDER_RE)
                    self.assertIn(
                        border,
                        ("1px solid #fff", "1px solid #ffffff", "1px solid white"),
                        "%s must carry a 1px white ring on all four sides" % selector,
                    )

    def test_the_systray_counters_carry_no_ring(self):
        """The counters are the plain identity-purple badge core draws: no rule of the cluster gives
        the navbar counters or the chat-window header counter a border or a ring. Both sit on the
        teal chrome, and the counter of the header belongs to the same family as the sidebar ones.
        The ring of a call glyph is not a counter and stays."""
        for bundle in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._compiled_css(bundle)
            for counter in (
                ".o-mail-MessagingMenuInDropdown-counter", ".o-mail-ActivityMenu-counter",
                ".o-mail-ChatWindow-counter",
            ):
                with self.subTest(bundle=bundle, counter=counter):
                    bodies = _bodies_matching(
                        css, lambda token, counter=counter: token.endswith(counter), ANY_ANCESTORS,
                    )
                    self.assertEqual(
                        _declared_values(bodies, _BORDER_RE), [],
                        "a rule gives %s a border or ring in %s" % (counter, bundle),
                    )

    def test_the_chat_window_caret_is_not_faded_on_the_teal_header(self):
        selector = (
            ".o-mail-ChatWindow-moreActions:not(.o-active):not(.o-hover) "
            "[data-icon=arrow_drop_down]"
        )
        for bundle in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._compiled_css(bundle)
            with self.subTest(bundle=bundle):
                bodies = _bodies_matching(
                    css, lambda token: token.replace('"', "") == selector, ANY_ANCESTORS,
                )
                opacities = _declared_values(bodies, _OPACITY_RE)
                self.assertTrue(opacities, "no compiled rule of %r declares an opacity" % selector)
                self.assertEqual(opacities[-1], "1")
