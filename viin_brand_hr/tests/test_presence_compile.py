# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# The "absent" dot of the employee presence widget in the light and the dark backend bundle. The
# compiled CSS is read, because the colour reaches the pixel through a bundle-specific compile.
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

# The amber of the "away" presence glyph of Discuss on a white page, and the warning fill on the dark one.
ABSENT_LIGHT = "#b27400"
ABSENT_DARK = "#ffcc32"
STYLESHEET = "viin_brand_hr/static/src/scss/hr.scss"

ABSENT_DOT = {
    "classes": frozenset({"o_icon_employee_absent"}),
    "ancestors": frozenset({"o_web_client"}),
    "prev_sibling": frozenset(),
}


@tagged("post_install", "-at_install")
class TestPresenceCompile(TransactionCase):

    def _absent_colour(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join((attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments)
        value = _computed_value(_COMMENT_RE.sub("", css), [ABSENT_DOT], ("color",))
        self.assertIsNotNone(value, "No compiled colour applies to the absent dot of %s." % bundle_name)
        return _normalize_colour(value)

    def test_absent_dot_is_the_amber_on_white_and_the_warning_fill_in_dark(self):
        """The "absent" dot is the amber of the "away" glyph on the white page (3.90:1, where core's
        warning fill is 1.51:1) and the warning fill on the dark one.

        WOULD FAIL IF REVERTED: without the stylesheet the dot keeps core's `$warning` on white;
        without the dark arm of the token it keeps the dull amber in dark."""
        self.assertEqual(self._absent_colour(BACKEND_BUNDLE), ABSENT_LIGHT)
        self.assertEqual(self._absent_colour(DARK_BUNDLE), ABSENT_DARK)

    def test_the_stylesheet_reads_the_token_and_holds_no_colour_literal(self):
        """The amber is the token of viin_brand, not a copy of its hex.

        WOULD FAIL IF REVERTED: a literal colour in the stylesheet."""
        with open(file_path(STYLESHEET), encoding="utf-8") as scss:
            code = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", scss.read(), flags=re.DOTALL))
        self.assertIn("$o-viin-status-away", code)
        self.assertNotRegex(code, r"#[0-9A-Fa-f]{3,8}\b")
