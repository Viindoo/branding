# A11y focus-ring contrast guard (PR #658 review-fix C-7; ODOO-AI-ETHOS #8; WCAG 2.1 SC 1.4.11).
#
# WHAT IS PROTECTED (behaviour, not code): viin_brand_common - the always-installed base - defines
# a shared focus-ring token applied to core interactive elements on :focus-visible, and that ring
# must be a VISIBLE indicator (WCAG SC 1.4.11 non-text contrast >= 3:1) against its surround in
# BOTH schemes. The review found 35/44 tab stops fail >= 3:1 in dark and that form inputs show zero
# focus change; the base owns the ring so an UNTHEMED install is accessible too (the redesign theme
# only wires its own shell widgets on top).
#
# WHY COMPILED CSS, NOT SOURCE: the ring colour reaches the pixel as a custom property that resolves
# per bundle - the light value in web.assets_backend and the dark arm in web.assets_web_dark (the
# recompiled dark bundle). A source-substring check would stay green after core/cluster renamed the
# token or dropped it from one bundle. So the token is read out of each compiled bundle and its
# contrast measured against the surface it rings.
#
# WHY 3:1 AND NOT 4.5:1: a focus ring is a NON-TEXT UI-component boundary, governed by SC 1.4.11
# (3:1), not the normal-text SC 1.4.3 (4.5:1). The threshold is the single SSOT WCAG_NON_TEXT_MIN
# in tests/test_brand_cascade_compile.py.
import re

from odoo.tests.common import TransactionCase, tagged

# WCAG helpers + surface constants are owned by the cascade suite (SSOT); imported, never
# re-literalised. That module does not import this one, so there is no import cycle.
from .test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BODY_BG,
    DARK_BUNDLE,
    WCAG_NON_TEXT_MIN,
    WHITE,
    _contrast_ratio,
    _normalize_colour,
)

# The shared focus-ring token the base defines (design C-7). Declared here as the one place the test
# names it; if the coder ships a differently-named token, this guard fails loudly and is re-grounded
# rather than silently passing on a dead name.
FOCUS_RING_TOKEN = "o-viin-focus"

# Every `--o-viin-focus: <value>` declaration, wherever it is declared (:root, .o_web_client, or a
# :focus-visible rule). The `\s*:` guard keeps `--o-viin-focus` from matching a longer sibling.
_FOCUS_DECL_RE = re.compile(r"--%s\s*:\s*([^;}]+)" % re.escape(FOCUS_RING_TOKEN))


@tagged("post_install", "-at_install")
class FocusRingCompileTest(TransactionCase):

    def _compiled_css(self, bundle_name):
        """Compile an asset bundle by name and return its CSS payload as decoded text."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so the focus-ring token cannot "
            "be verified." % bundle_name,
        )
        return css

    def _focus_ring_colour(self, css, bundle_name):
        """Return the effective focus-ring colour declared in ``css``, failing loudly when absent."""
        hexes = [c for c in (_normalize_colour(v) for v in _FOCUS_DECL_RE.findall(css)) if c]
        self.assertTrue(
            hexes,
            "No --%s focus-ring token resolves to a colour in the %s bundle. The base a11y focus "
            "ring (focus_ring.scss) is missing from this bundle, so interactive elements have no "
            "visible >= 3:1 focus indicator there." % (FOCUS_RING_TOKEN, bundle_name),
        )
        # Equal-scope declarations: the last in source order is the effective one.
        return hexes[-1]

    def test_focus_ring_token_clears_non_text_contrast_in_light_scheme(self):
        """The focus ring must clear WCAG 3:1 against the light backend surface (white).

        RED BEFORE GREEN: no focus_ring.scss / --o-viin-focus token exists yet, so the token is
        absent from web.assets_backend and this fails; it passes once the base ring lands (design
        light value #005E68, 7.5:1 on white)."""
        css = self._compiled_css(BACKEND_BUNDLE)
        ring = self._focus_ring_colour(css, BACKEND_BUNDLE)
        ratio = _contrast_ratio(ring, WHITE)
        self.assertGreaterEqual(
            ratio, WCAG_NON_TEXT_MIN,
            "The focus ring --%s=%s clears only %.2f:1 against the light surface %s, below the WCAG "
            "SC 1.4.11 non-text threshold of %.1f:1 - the ring is not a visible focus indicator in "
            "light mode." % (FOCUS_RING_TOKEN, ring, ratio, WHITE, WCAG_NON_TEXT_MIN),
        )

    def test_focus_ring_token_clears_non_text_contrast_in_dark_scheme(self):
        """The focus ring must clear WCAG 3:1 against the dark panel #111B1E.

        RED BEFORE GREEN: web.assets_web_dark carries no --o-viin-focus dark arm yet (and no light
        one either), so the token is absent and this fails; it passes once the dark arm lands
        (design dark value #7FE0EA on #111B1E). This is the 35/44-dark-tab-stops regression guard."""
        css = self._compiled_css(DARK_BUNDLE)
        ring = self._focus_ring_colour(css, DARK_BUNDLE)
        ratio = _contrast_ratio(ring, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_NON_TEXT_MIN,
            "The focus ring --%s=%s clears only %.2f:1 against the dark panel %s, below the WCAG SC "
            "1.4.11 non-text threshold of %.1f:1 - focus is invisible in dark mode (the review's "
            "35/44-failing-tab-stops defect)."
            % (FOCUS_RING_TOKEN, ring, ratio, DARK_BODY_BG, WCAG_NON_TEXT_MIN),
        )

    def test_focus_ring_token_is_actually_applied_to_interactive_elements(self):
        """The ring token must be REFERENCED (via var()) so it is a real outline, not a dead token.

        Non-vacuity: a declared token nobody reads would let the contrast guards pass on a ring that
        never paints. The Python layer confirms the token is wired into an outline/box-shadow; the
        per-element focus behaviour (focusing an input shows the ring) is the sibling Hoot test's job.

        RED BEFORE GREEN: with no focus_ring.scss the token is neither declared nor referenced."""
        css = self._compiled_css(BACKEND_BUNDLE)
        self.assertIn(
            "var(--%s" % FOCUS_RING_TOKEN, css,
            "The focus-ring token --%s is never referenced via var() in web.assets_backend, so no "
            "interactive element actually renders the ring. focus_ring.scss must apply it (e.g. "
            "`outline: 2px solid var(--%s)`) on :focus-visible." % (FOCUS_RING_TOKEN, FOCUS_RING_TOKEN),
        )
