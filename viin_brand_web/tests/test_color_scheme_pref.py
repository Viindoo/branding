# Dark-mode preference + server resolution guards (ODOO-AI-ETHOS #8: protect the
# BEHAVIOR/contract, not the code).
#
# OWNERSHIP (PR #658 review-fix C-1): the per-user color-scheme preference AND the server-side
# ir.http.color_scheme() resolver now live in viin_brand_common - the ALWAYS-installed brand base -
# so dark mode resolves server-side even on a database WITHOUT the redesign theme
# (viin_backend_theme). This suite was relocated here from viin_backend_theme/tests/test_theme_prefs.py
# because the base now OWNS the field + method, so the base owns their behavior test.
#
# WHAT IS PROTECTED
#  1. res.users.viin_color_scheme is a per-user Selection (light/dark/auto, default light).
#  2. SECURITY: it is SELF-writeable - a plain internal user sets their OWN preference with no admin
#     rights, but writing ANOTHER user's preference still raises AccessError. This is the ONLY
#     security surface of the dark-mode feature (no ir.model.access / ir.rule / sudo), so the SELF
#     scope is exactly what must be asserted - a regression that widened it (e.g. adding the field to
#     a group-write path) would silently let any user flip other users' UI.
#  3. ir.http.color_scheme() resolution order: request `color_scheme` cookie (explicit light/dark)
#     > stored res.users.viin_color_scheme (explicit light/dark) > super() as the final fallback.
#     'auto' is NEVER forced server-side - it falls through to super() so the client / OS decides.
#     The method always returns a value (never a missing return). The cookie branch is exercised by
#     patching the module-level `request` (the method reads request.httprequest.cookies).
from unittest.mock import patch

from odoo.tests.common import TransactionCase, new_test_user, tagged
from odoo.exceptions import AccessError

# The module path whose `request` symbol color_scheme() reads. Patched (not the global
# odoo.http.request) so the cookie branch is exercised without a live HTTP request.
_IR_HTTP_MODULE = "odoo.addons.viin_brand_common.models.ir_http"


class _FakeHttpRequest:
    """Minimal stand-in for odoo.http.request exposing only .httprequest.cookies.get()."""

    def __init__(self, cookies):
        self.httprequest = type("_HR", (), {"cookies": dict(cookies)})()


@tagged("post_install", "-at_install")
class TestViinColorSchemePref(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = new_test_user(cls.env, login="viin_pref_a", groups="base.group_user")
        cls.user_b = new_test_user(cls.env, login="viin_pref_b", groups="base.group_user")

    def test_field_shape_and_default(self):
        """The preference is a light/dark/auto Selection defaulting to light."""
        field = self.env["res.users"]._fields.get("viin_color_scheme")
        self.assertIsNotNone(
            field,
            "res.users.viin_color_scheme was not added by viin_brand_common (the base that owns the "
            "dark-mode preference).",
        )
        self.assertEqual(
            {key for key, _label in field.selection}, {"light", "dark", "auto"},
            "viin_color_scheme must offer exactly light/dark/auto.",
        )
        self.assertEqual(
            self.user_a.viin_color_scheme, "light",
            "viin_color_scheme must default to 'light'.",
        )

    def test_user_sets_own_scheme_without_admin(self):
        """A non-admin internal user writes their OWN scheme (SELF_WRITEABLE) - no admin rights."""
        self.user_a.with_user(self.user_a).write({"viin_color_scheme": "dark"})
        self.assertEqual(self.user_a.viin_color_scheme, "dark")

    def test_user_cannot_write_another_users_scheme(self):
        """Writing ANOTHER user's scheme must raise AccessError - SELF scope, not a broad grant."""
        with self.assertRaises(AccessError):
            self.user_b.with_user(self.user_a).write({"viin_color_scheme": "dark"})

    def test_color_scheme_cookie_overrides_everything(self):
        """An explicit `color_scheme` cookie wins over the stored preference and over super().

        The cookie is the per-request choice the toggle sets before a reload; it must beat the
        persisted preference so a just-changed scheme takes effect on the next request."""
        ir_http = self.env["ir.http"]
        # Stored preference is the OPPOSITE of the cookie, proving the cookie wins.
        self.env.user.viin_color_scheme = "light"
        with patch(_IR_HTTP_MODULE + ".request", _FakeHttpRequest({"color_scheme": "dark"})):
            self.assertEqual(
                ir_http.color_scheme(), "dark",
                "A `color_scheme=dark` cookie must resolve to 'dark' even when the stored "
                "preference is 'light'.",
            )
        self.env.user.viin_color_scheme = "dark"
        with patch(_IR_HTTP_MODULE + ".request", _FakeHttpRequest({"color_scheme": "light"})):
            self.assertEqual(
                ir_http.color_scheme(), "light",
                "A `color_scheme=light` cookie must resolve to 'light' even when the stored "
                "preference is 'dark'.",
            )

    def test_color_scheme_falls_back_to_stored_preference_without_cookie(self):
        """With no cookie, color_scheme() returns the user's explicit light/dark preference."""
        ir_http = self.env["ir.http"]
        # No cookie at all (request absent) - only the stored preference decides.
        with patch(_IR_HTTP_MODULE + ".request", None):
            self.env.user.viin_color_scheme = "dark"
            self.assertEqual(ir_http.color_scheme(), "dark")
            self.env.user.viin_color_scheme = "light"
            self.assertEqual(ir_http.color_scheme(), "light")

    def test_color_scheme_auto_defers_to_super_light(self):
        """'auto' (and any unset value) must fall through to super() - never forced dark server-side.

        The server keeps rendering core's default ('light') for 'auto'; the client / OS then decides
        via the boot reflection. This is the invariant that keeps 'auto' a CLIENT decision, so a
        regression that resolved 'auto' to 'dark' on the server would be caught here."""
        ir_http = self.env["ir.http"]
        with patch(_IR_HTTP_MODULE + ".request", None):
            self.env.user.viin_color_scheme = "auto"
            self.assertEqual(
                ir_http.color_scheme(), "light",
                "'auto' must defer to super() (core default 'light'), not be forced to a scheme "
                "server-side.",
            )
