# Dark-mode preference + server resolution guards (ODOO-AI-ETHOS #8: protect the
# BEHAVIOR/contract, not the code).
#
# OWNERSHIP (PR #658 review-fix C-1): the per-user color-scheme preference AND the server-side
# ir.http.color_scheme() resolver now live in viin_brand_web - the ALWAYS-installed brand base -
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
#  3. ir.http.color_scheme() resolution order: the user's own explicit light/dark
#     res.users.viin_color_scheme > the request `color_scheme` cookie > super() as the final
#     fallback. The cookie ranks BELOW an explicit preference because it is per-BROWSER while the
#     preference is per-USER. It ranks ABOVE super() only so that 'auto' works: the server cannot
#     read the OS, so the client resolves 'auto' and caches the effective light|dark in that same
#     cookie. 'auto' is still never FORCED server-side - with no cached resolution it falls to
#     super(). The method always returns a value (never a missing return). The cookie branch is
#     exercised by patching the module-level `request` (it reads request.httprequest.cookies).
from unittest.mock import patch

from odoo.tests.common import TransactionCase, new_test_user, tagged
from odoo.exceptions import AccessError

# The module path whose `request` symbol color_scheme() reads. Patched (not the global
# odoo.http.request) so the cookie branch is exercised without a live HTTP request.
_IR_HTTP_MODULE = "odoo.addons.viin_brand_web.models.ir_http"


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
            "res.users.viin_color_scheme was not added by viin_brand_web (the base that owns the "
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

    def test_explicit_preference_outranks_a_browser_cookie(self):
        """A user's own explicit light/dark preference decides, even against a contrary cookie.

        The preference is per-USER; the `color_scheme` cookie is per-BROWSER and outlives the
        session that wrote it. Were the cookie to win, whoever used a shared browser last would
        choose the scheme for whoever logs in next, for that cookie's whole lifetime."""
        ir_http = self.env["ir.http"]
        self.env.user.viin_color_scheme = "light"
        with patch(_IR_HTTP_MODULE + ".request", _FakeHttpRequest({"color_scheme": "dark"})):
            self.assertEqual(
                ir_http.color_scheme(), "light",
                "A stored 'light' preference must survive a contrary `color_scheme=dark` cookie.",
            )
        self.env.user.viin_color_scheme = "dark"
        with patch(_IR_HTTP_MODULE + ".request", _FakeHttpRequest({"color_scheme": "light"})):
            self.assertEqual(
                ir_http.color_scheme(), "dark",
                "A stored 'dark' preference must survive a contrary `color_scheme=light` cookie.",
            )

    def test_auto_resolves_from_the_client_cached_cookie(self):
        """Under 'auto' the cookie decides - it is the only place the OS resolution exists.

        The server cannot read the device preference. The client resolves 'auto' via matchMedia
        and caches the effective light|dark in the same `color_scheme` cookie, so for 'auto' -
        and only for 'auto' - that cookie is what the server must honour."""
        ir_http = self.env["ir.http"]
        self.env.user.viin_color_scheme = "auto"
        with patch(_IR_HTTP_MODULE + ".request", _FakeHttpRequest({"color_scheme": "dark"})):
            self.assertEqual(
                ir_http.color_scheme(), "dark",
                "With preference 'auto', a cached `color_scheme=dark` must resolve to 'dark'.",
            )
        with patch(_IR_HTTP_MODULE + ".request", _FakeHttpRequest({"color_scheme": "light"})):
            self.assertEqual(
                ir_http.color_scheme(), "light",
                "With preference 'auto', a cached `color_scheme=light` must resolve to 'light'.",
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
        """'auto' with no cached resolution falls through to super() - never forced server-side.

        Until the client has resolved the OS and cached it in the cookie, the server has nothing
        to go on and keeps rendering core's default ('light'). This is the invariant that keeps
        'auto' a CLIENT decision, so a regression that guessed 'dark' server-side is caught here."""
        ir_http = self.env["ir.http"]
        with patch(_IR_HTTP_MODULE + ".request", None):
            self.env.user.viin_color_scheme = "auto"
            self.assertEqual(
                ir_http.color_scheme(), "light",
                "'auto' must defer to super() (core default 'light'), not be forced to a scheme "
                "server-side.",
            )
