import re

from odoo.tests.common import TransactionCase, tagged

# Bundles that carry this module's SCSS and have no compile guard elsewhere. `web.assets_backend`
# is guarded by test_brand_cascade_compile.py, and the private `web._assets_primary_variables` is
# compiled through the two dark bundles, since it cannot compile alone (its Sass functions live
# in `web._assets_helpers`).
CSS_BUNDLES = (
    "web.assets_web_dark",
    "web.assets_backend_lazy_dark",
)

# Bundles that carry this module's test files only.
JS_BUNDLES = (
    "web.assets_unit_tests",
    "web.assets_tests",
)

# A listed JS file that is gone is not raised: the bundle embeds a `console.error` carrying
# `in file '<url>'`, and only this module's own url prefix is matched, so another module's noise
# cannot fail the test.
_MISSING_OWN_ASSET_RE = re.compile(r"in file 'viin_brand/[\w./-]{0,200}'")


@tagged("post_install", "-at_install")
class TestBrandBundleCompile(TransactionCase):
    """Every bundle this module contributes to resolves and compiles with this module's files in it.

    Odoo checks neither an asset anchor nor a listed file at install time: a renamed anchor raises
    only when the bundle is resolved, a missing SCSS file lands in ``css_errors`` and a missing JS
    file becomes an embedded ``console.error``. A bundle that merely compiles therefore proves
    nothing; these tests check that this module's own content landed in it.
    """

    def _compiled_js(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(
            bundle_name, css=False, js=True, debug_assets=True,
        )
        return (bundle.js().raw or b"").decode("utf-8", "replace")

    def test_backend_bundle_carries_the_webclient_favicon_patch(self):
        self.assertIn("/web/image/res.company/", self._compiled_js("web.assets_backend"))

    def test_backend_bundle_carries_the_settings_page_icon_patch(self):
        self.assertIn("get_viin_brand_modules_icon", self._compiled_js("web.assets_backend"))

    def test_backend_bundle_carries_the_settings_page_template_extension(self):
        self.assertIn(
            'registerTemplateExtension("web.SettingsPage"', self._compiled_js("web.assets_backend"),
        )

    def test_css_bundles_compile_without_errors(self):
        """The dark bundles compile to real CSS, and not to a cached CSS-error fallback.

        ``css()`` returns an already cached attachment without repopulating ``css_errors``, so the
        payload is checked for the error markers as well.
        """
        for bundle_name in CSS_BUNDLES:
            with self.subTest(bundle=bundle_name):
                bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
                attachments = bundle.css() or self.env["ir.attachment"]
                css = "".join(
                    (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
                )
                self.assertFalse(
                    bundle.css_errors,
                    "%s reported SCSS compile errors: %s" % (bundle_name, "; ".join(bundle.css_errors)),
                )
                self.assertTrue(css.strip(), "%s compiled to empty CSS." % bundle_name)
                for marker in ("## CSS error message ##", "css_error_message", "A css error occured"):
                    self.assertNotIn(marker, css, "%s served a cached CSS-error payload." % bundle_name)

    def test_js_bundles_build_with_no_missing_asset(self):
        """The test bundles resolve every file this module lists in them."""
        for bundle_name in JS_BUNDLES:
            with self.subTest(bundle=bundle_name):
                bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=False, js=True)
                js_attachment = bundle.js()
                self.assertTrue(js_attachment, "%s did not produce a JS attachment." % bundle_name)
                js = (js_attachment.raw or b"").decode("utf-8", "replace")
                match = _MISSING_OWN_ASSET_RE.search(js)
                self.assertIsNone(
                    match,
                    "%s embeds a missing-asset error: %r" % (bundle_name, match and match.group(0)),
                )
