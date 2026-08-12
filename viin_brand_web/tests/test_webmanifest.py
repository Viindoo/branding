from odoo.tests.common import tagged
from odoo.tools import file_path

from odoo.addons.web.tests.test_webmanifest import WebManifestRoutesTest

try:
    # RED now: the backend coder has not yet added the SSOT constant. Imported defensively so a
    # missing constant fails these tests crisply instead of breaking collection of the tests package.
    from ..controllers.webmanifest import VIINDOO_THEME_COLOR
except ImportError:
    VIINDOO_THEME_COLOR = None

# Filename stem shared by EVERY core Odoo PWA mascot asset
# (web/static/img/odoo-icon-192x192.png, -512x512.png, odoo-icon-ios.png). Asserting on the stem -
# not on one exact path - catches any of them leaking back into a de-branded surface.
ODOO_ICON_MARKER = "odoo-icon"

# The Viindoo asset core's `_icon_path()` fallback must resolve to once this module is installed.
# It is the fallback used by `_get_scoped_app_icons` for any app that ships no
# static/description/icon.svg, and therefore also what `/scoped_app_icon_png` (Safari's fixed-size
# PWA icon, i.e. the apple-touch-icon of the Install-App page) redirects to.
VIINDOO_FALLBACK_ICON_SRC = "/viin_brand_web/static/img/viindoo-icon-192x192.png"

# An app_id that deliberately ships NO static/description/icon.svg, so requesting it EXERCISES the
# `_icon_path()` fallback branch instead of the icon.svg branch. This module itself is the safest
# choice: it is always installed when these tests run. (`base`, used by the colour test below, DOES
# ship base/static/description/icon.svg and therefore never reaches the fallback - which is exactly
# why the pre-existing scoped test could not see the mascot leak.)
FALLBACK_ICON_APP_ID = "viin_brand_web"

# The `web.web_app_name` ir.config_parameter core reads for the PWA name, and a customer value used
# to prove it survives the de-brand.
WEB_APP_NAME_PARAM = "web.web_app_name"
CUSTOMER_APP_NAME = "Acme Portal"


@tagged("-at_install", "post_install")
class BrandWebManifestRoutesTest(WebManifestRoutesTest):
    """
    Skip odoo test and replace similar test for viindoo
    """

    def _assert_brand_color(self, value, label):
        """Assert a rendered manifest colour equals the ONE brand-hex SSOT (case-insensitive:
        JSON case may differ from the canonical #00BBCE)."""
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in viin_brand_web/controllers/webmanifest.py "
            "(single Python brand-hex SSOT).",
        )
        self.assertEqual(
            (value or "").lower(), VIINDOO_THEME_COLOR.lower(),
            "manifest %s must equal the brand SSOT VIINDOO_THEME_COLOR=%s (got %r)"
            % (label, VIINDOO_THEME_COLOR, value),
        )

    def test_brand_webmanifest(self):
        """
        This route returns a well formed backend's WebManifest
        """
        self.authenticate("admin", "admin")
        response = self.url_open("/web/manifest.webmanifest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/manifest+json")
        data = response.json()
        self.assertEqual(data["name"], "Viindoo")
        self.assertEqual(data["scope"], "/odoo")
        self.assertEqual(data["start_url"], "/odoo")
        self.assertEqual(data["display"], "standalone")
        self._assert_brand_color(data["background_color"], "background_color")
        self._assert_brand_color(data["theme_color"], "theme_color")
        self.assertEqual(data["prefer_related_applications"], False)
        self.assertCountEqual(data["icons"], [
            {'src': '/viin_brand_web/static/img/viindoo-icon-192x192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': '/viin_brand_web/static/img/viindoo-icon-512x512.png', 'sizes': '512x512', 'type': 'image/png'}
        ])
        self.assertGreaterEqual(len(data["shortcuts"]), 0)
        for shortcut in data["shortcuts"]:
            self.assertGreater(len(shortcut["name"]), 0)
            self.assertGreater(len(shortcut["description"]), 0)
            self.assertGreater(len(shortcut["icons"]), 0)
            self.assertTrue(shortcut["url"].startswith("/odoo?menu_id="))

    def test_brand_webmanifest_unauthenticated(self):
        """
        This route returns a well formed backend's WebManifest
        """
        response = self.url_open("/web/manifest.webmanifest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/manifest+json")
        data = response.json()
        self.assertEqual(data["name"], "Viindoo")
        self.assertEqual(data["scope"], "/odoo")
        self.assertEqual(data["start_url"], "/odoo")
        self.assertEqual(data["display"], "standalone")
        self._assert_brand_color(data["background_color"], "background_color")
        self._assert_brand_color(data["theme_color"], "theme_color")
        self.assertEqual(data["prefer_related_applications"], False)
        self.assertCountEqual(data["icons"], [
            {'src': '/viin_brand_web/static/img/viindoo-icon-192x192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': '/viin_brand_web/static/img/viindoo-icon-512x512.png', 'sizes': '512x512', 'type': 'image/png'}
        ])
        self.assertEqual(len(data["shortcuts"]), 0)

    def _assert_no_odoo_icon(self, icons, label):
        """Assert no core Odoo mascot asset appears among a manifest's ``icons`` entries."""
        sources = [icon.get("src") or "" for icon in icons]
        self.assertTrue(sources, "%s must declare at least one icon to brand-check" % label)
        for src in sources:
            self.assertNotIn(
                ODOO_ICON_MARKER, src,
                "%s still serves a core Odoo mascot asset (%r among %r). Every PWA icon surface "
                "must resolve to a Viindoo asset once this module is installed."
                % (label, src, sources),
            )

    def test_brand_scoped_webmanifest_debranded(self):
        """
        The scoped-app PWA manifest is de-branded from the SAME brand SSOT (DESIGN 4a).
        In core 19.0 the scoped manifest dict is built inline in the `scoped_app_manifest` route
        (hardcoding #714B67); the module must re-point it so theme/background come from the SSOT.

        Also guards the ICONS, not just the two colours: an app that ships its own
        static/description/icon.svg (``base`` does) must keep serving that icon and never a core
        Odoo mascot asset. The fallback branch - the one that actually leaked - is covered by
        `test_brand_scoped_webmanifest_icon_fallback_is_debranded` below.
        """
        self.authenticate("admin", "admin")
        response = self.url_open(
            "/web/manifest.scoped_app_manifest?app_id=base&path=%2Fodoo%2Fbase&app_name=Base"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/manifest+json")
        data = response.json()
        self._assert_brand_color(data["background_color"], "scoped background_color")
        self._assert_brand_color(data["theme_color"], "scoped theme_color")
        self._assert_no_odoo_icon(data["icons"], "scoped manifest icons (app_id=base)")

    def test_brand_scoped_webmanifest_icon_fallback_is_debranded(self):
        """The scoped manifest's ICON FALLBACK must be the Viindoo asset, never the Odoo mascot.

        Core `_get_scoped_app_icons` falls back to `_icon_path()` for every app that ships no
        `static/description/icon.svg`, and core `_icon_path()` returns
        `web/static/img/odoo-icon-192x192.png`. On a de-branded database that fallback is the
        live leak: the Install-App page of any such app renders the Odoo mascot. This asserts the
        OBSERVABLE manifest payload for an app that provably takes the fallback branch."""
        self.authenticate("admin", "admin")

        # Precondition, asserted rather than assumed: the chosen app_id must genuinely have no
        # icon.svg, otherwise this test would silently stop exercising the fallback branch.
        with self.assertRaises(
            FileNotFoundError,
            msg="%s now ships static/description/icon.svg, so it no longer exercises the "
                "`_icon_path()` fallback - pick another app_id for this test."
                % FALLBACK_ICON_APP_ID,
        ):
            file_path("%s/static/description/icon.svg" % FALLBACK_ICON_APP_ID)

        response = self.url_open(
            "/web/manifest.scoped_app_manifest?app_id=%s&path=%%2Fodoo&app_name=Viindoo"
            % FALLBACK_ICON_APP_ID
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self._assert_no_odoo_icon(
            data["icons"], "scoped manifest icons (fallback app_id=%s)" % FALLBACK_ICON_APP_ID
        )
        self.assertEqual(
            [icon["src"] for icon in data["icons"]], [VIINDOO_FALLBACK_ICON_SRC],
            "the scoped-manifest icon fallback must be the Viindoo asset %s (got %r)"
            % (VIINDOO_FALLBACK_ICON_SRC, data["icons"]),
        )

    def test_scoped_app_page_apple_touch_icon_is_debranded(self):
        """The Install-App page and the Safari PNG icon it points at must carry no Odoo mascot.

        Core renders that page from `web.webclient_scoped_app`, whose apple-touch-icon href is the
        `/scoped_app_icon_png` route; that route resolves its bytes through
        `_get_scoped_app_icons` -> `_icon_path()`. So the page is only de-branded when the whole
        chain is - this walks it end to end rather than trusting the page HTML alone."""
        self.authenticate("admin", "admin")

        page = self.url_open(
            "/scoped_app?app_id=%s&path=odoo&app_name=Viindoo" % FALLBACK_ICON_APP_ID
        )
        self.assertEqual(page.status_code, 200, "the Install-App page must render")
        self.assertNotIn(
            ODOO_ICON_MARKER, page.text,
            "the Install-App page still references a core Odoo mascot asset (%r)."
            % ODOO_ICON_MARKER,
        )

        # The apple-touch-icon href itself: follow it one hop and check what it actually serves.
        icon_response = self.url_open(
            "/scoped_app_icon_png?app_id=%s" % FALLBACK_ICON_APP_ID, allow_redirects=False
        )
        location = icon_response.headers.get("Location", "")
        self.assertNotIn(
            ODOO_ICON_MARKER, location,
            "the apple-touch-icon route /scoped_app_icon_png still resolves to a core Odoo mascot "
            "asset (%r). `_icon_path()` must return the Viindoo icon." % location,
        )
        self.assertIn(
            VIINDOO_FALLBACK_ICON_SRC, location,
            "the apple-touch-icon route must resolve to the Viindoo asset %s (got %r)."
            % (VIINDOO_FALLBACK_ICON_SRC, location),
        )

    def test_pwa_app_name_debrands_the_untouched_odoo_default(self):
        """An untouched `web.web_app_name` (core's stock 'Odoo') must be de-branded to Viindoo.

        Asserts the STOCK-VALUE branch explicitly - `test_brand_webmanifest` above only covers the
        unset-parameter case, which reaches the same default through core's `get_param` fallback."""
        self.env["ir.config_parameter"].sudo().set_param(WEB_APP_NAME_PARAM, "Odoo")
        self.env.flush_all()

        self.authenticate("admin", "admin")
        response = self.url_open("/web/manifest.webmanifest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["name"], "Viindoo",
            "a `web.web_app_name` still holding core's stock 'Odoo' must be de-branded.",
        )

    def test_pwa_app_name_preserves_a_customer_configured_name(self):
        """A customer-configured `web.web_app_name` must SURVIVE the de-brand.

        Core resolves the PWA name from the `web.web_app_name` ir.config_parameter, so a blanket
        overwrite silently destroys a customer's own PWA app name on every manifest fetch - a
        functional regression, not a de-brand. Only the untouched Odoo default may be replaced."""
        self.env["ir.config_parameter"].sudo().set_param(WEB_APP_NAME_PARAM, CUSTOMER_APP_NAME)
        self.env.flush_all()

        self.authenticate("admin", "admin")
        response = self.url_open("/web/manifest.webmanifest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["name"], CUSTOMER_APP_NAME,
            "a customer-configured `%s` must be preserved, not overwritten with the brand name."
            % WEB_APP_NAME_PARAM,
        )

    def test_brand_apple_touch_icon(self):
        """
        This request tests the presence of an apple-touch-icon image route for the PWA icon and
        its presence from the head of the document.
        """
        self.authenticate("demo", "demo")
        response = self.url_open("/viin_brand_web/static/img/viindoo-icon-ios.png")
        self.assertEqual(response.status_code, 200)

        document = self.url_open("/web")
        self.assertIn(
            '<link rel="apple-touch-icon" href="/viin_brand_web/static/img/viindoo-icon-ios.png"/>', document.text,
            "Icon for iOS is present in the head of the document.",
        )
