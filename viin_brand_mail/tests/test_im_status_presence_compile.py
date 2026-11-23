# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# The colour of the presence glyph (`.o-mail-ImStatus`) in the light and the dark backend bundle:
# online and bot are the success green of the product, away is the amber, busy and offline are
# core's, and on the teal frame (the navbar avatar, the header of a floating chat window) each state
# takes a light tint. The compiled CSS is read, because the colours reach the pixel through
# bundle-specific compiles; every expected value is a literal of the design.
import re

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_path

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BUNDLE,
    _COMMENT_RE,
    _computed_value,
    _normalize_colour,
)

# state -> the colour class core stamps on the glyph element itself (mail im_status.js `colorClass`)
STATE_CLASSES = {
    "online": ("text-success",),
    "bot": ("text-success",),
    "away": ("o-yellow",),
    "busy": ("text-danger",),
    "offline": ("text-700", "opacity-75"),
}
GLYPH_BASE = ("oi", "o-mail-ImStatus", "d-flex")
CONTENT = frozenset({"o_web_client"})
NAVBAR = frozenset({"o_web_client", "o_main_navbar"})
CHAT_WINDOW_HEADER = frozenset({"o_web_client", "o-mail-ChatWindow", "o-mail-ChatWindow-header"})

# the colour of each state on a content surface, per scheme
SUCCESS_GREEN = "#00884d"
SUCCESS_GREEN_DARK = "#4dac82"
AWAY_AMBER = "#b27400"
WARNING_FILL = "#ffcc32"
# the tint of each state on the teal frame, the same in both schemes
CHROME_TINTS = {
    "online": "#4ade80",
    "bot": "#4ade80",
    "away": WARNING_FILL,
    "busy": "#ff8a85",
    "offline": "#dde6e8",
}

# The token of every presence hex is declared in viin_brand; the stylesheet of this module reads them.
TINT_TOKEN_SOURCE = "viin_brand/static/src/scss/brand_variables.scss"
STYLESHEET = "viin_brand_mail/static/src/core/common/im_status.scss"


def _glyph(state, ancestors):
    classes = frozenset(GLYPH_BASE + STATE_CLASSES[state])
    return {"classes": classes, "ancestors": ancestors, "prev_sibling": frozenset()}


@tagged("post_install", "-at_install")
class TestImStatusPresenceCompile(TransactionCase):

    def _css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join((attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments)
        self.assertTrue(css.strip(), "%s compiled to empty CSS." % bundle_name)
        return _COMMENT_RE.sub("", css)

    def _colour(self, css, element, prop="color"):
        value = _computed_value(css, [element], (prop,))
        self.assertIsNotNone(value, "No compiled declaration of %s applies to %s" % (prop, element["classes"]))
        return _normalize_colour(value) if prop == "color" else value

    def test_online_and_bot_are_the_success_green_in_both_schemes(self):
        """The online and bot glyphs read the success green of the product: #00884D in light and its
        lightened arm in dark, the same value as the other `.text-success` of the product (the status
        picker, the avatar card, the employee card), never the brand purple or cyan.

        WOULD FAIL IF REVERTED: a rule that repaints `.o-mail-ImStatus.text-success` with the action
        colour, or a success text colour that is not the success fill."""
        for scheme, bundle, expected in (
            ("light", BACKEND_BUNDLE, SUCCESS_GREEN), ("dark", DARK_BUNDLE, SUCCESS_GREEN_DARK),
        ):
            css = self._css(bundle)
            picker_row = {
                "classes": frozenset({"oi", "text-success"}), "ancestors": CONTENT,
                "prev_sibling": frozenset(),
            }
            self.assertEqual(self._colour(css, picker_row), expected, "picker row [%s]" % scheme)
            for state in ("online", "bot"):
                with self.subTest(scheme=scheme, state=state):
                    self.assertEqual(self._colour(css, _glyph(state, CONTENT)), expected)

    def test_away_is_one_amber_on_the_dot_and_the_picker_swatch_and_the_warning_fill_in_dark(self):
        """Away is #B27400 in light and the warning fill #FFCC32 in dark, on the dot and on the swatch
        of the status picker alike.

        WOULD FAIL IF REVERTED: dropping the dark arm of `$o-viin-status-away` leaves the dull amber
        in dark; a dot and a swatch that read different values desync the picker from the dot."""
        swatch = {
            "classes": frozenset({"oi", "o-yellow", "me-1"}),
            "ancestors": frozenset({
                "o_web_client", "o-mail-ImStatusDropdown", "o-dropdown--menu", "dropdown-menu", "show",
                "o-dropdown-item", "dropdown-item", "o-navigable",
            }),
            "prev_sibling": frozenset(),
        }
        for scheme, bundle, expected in (
            ("light", BACKEND_BUNDLE, AWAY_AMBER), ("dark", DARK_BUNDLE, WARNING_FILL),
        ):
            css = self._css(bundle)
            with self.subTest(scheme=scheme, site="dot"):
                self.assertEqual(self._colour(css, _glyph("away", CONTENT)), expected)
            with self.subTest(scheme=scheme, site="swatch"):
                self.assertEqual(self._colour(css, swatch), expected)

    def test_busy_and_offline_keep_the_colour_core_gives_them(self):
        """Busy and offline resolve to the colour of the bare core utility of their class, and the
        offline glyph keeps core's opacity: the module adds no rule for either on a content surface.

        WOULD FAIL IF REVERTED: an override such as the faint grey on `.text-700`, which is 1.69:1
        on white, makes the glyph differ from core's own `.text-700 opacity-75`."""
        for scheme, bundle in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._css(bundle)
            for state in ("busy", "offline"):
                with self.subTest(scheme=scheme, state=state):
                    bare = {
                        "classes": frozenset(STATE_CLASSES[state]), "ancestors": CONTENT,
                        "prev_sibling": frozenset(),
                    }
                    self.assertEqual(
                        self._colour(css, _glyph(state, CONTENT)), self._colour(css, bare),
                    )
            offline = _glyph("offline", CONTENT)
            self.assertEqual(self._colour(css, offline, "opacity"), "0.75")

    def test_each_state_reads_a_light_tint_on_the_teal_frame_in_both_schemes(self):
        """On the navbar and in the header of a chat window the glyph takes the tint of its state, the
        same in light and dark because the frame is the same; the offline tint is opaque.

        WOULD FAIL IF REVERTED: without the chrome block the online and busy glyphs fall under 2:1
        on the teal and the offline one is dimmed by `opacity-75`."""
        for scheme, bundle in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._css(bundle)
            for site, ancestors in (("navbar", NAVBAR), ("chat window header", CHAT_WINDOW_HEADER)):
                for state, tint in CHROME_TINTS.items():
                    with self.subTest(scheme=scheme, site=site, state=state):
                        self.assertEqual(self._colour(css, _glyph(state, ancestors)), tint)
                offline = _glyph("offline", ancestors)
                self.assertEqual(self._colour(css, offline, "opacity"), "1", "%s offline [%s]" % (site, scheme))

    def test_the_tints_do_not_leak_to_the_content_surface(self):
        """A glyph outside the frame never takes a tint of the frame.

        WOULD FAIL IF REVERTED: a chrome rule without its `.o_main_navbar` or chat-window scope."""
        css = self._css(BACKEND_BUNDLE)
        for state, tint in CHROME_TINTS.items():
            if state == "away":
                continue
            with self.subTest(state=state):
                self.assertNotEqual(self._colour(css, _glyph(state, CONTENT)), tint)

    def test_each_tint_is_declared_once_as_a_token(self):
        """Every presence hex of the design is spelled once in the SCSS sources, as the token the
        stylesheets read; the stylesheets themselves hold no colour literal.

        WOULD FAIL IF REVERTED: a tint or the amber copied into a rule instead of read from its
        token."""
        sources = {}
        for path in (TINT_TOKEN_SOURCE, STYLESHEET):
            with open(file_path(path), encoding="utf-8") as scss:
                sources[path] = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", scss.read(), flags=re.DOTALL))
        for hexcode in (AWAY_AMBER, CHROME_TINTS["online"], CHROME_TINTS["busy"], CHROME_TINTS["offline"]):
            with self.subTest(hex=hexcode):
                count = sum(text.lower().count(hexcode) for text in sources.values())
                self.assertEqual(count, 1, "%s is spelled %d times in the presence stylesheets" % (hexcode, count))
                self.assertIn(hexcode, sources[TINT_TOKEN_SOURCE].lower())
        self.assertNotRegex(sources[STYLESHEET], r"#[0-9A-Fa-f]{3,8}\b")
