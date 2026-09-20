# D2-A bundle-compile requirement (the "asset anchors are validated lazily" finding) - protects
# the business rule: "every asset anchor and SCSS contribution this module makes to a bundle
# resolves and compiles cleanly." Odoo validates NEITHER at install time, verified against
# odoo/addons/base/models/:
#   * a ('before'/'after'/'replace', anchor, source) directive resolves its ANCHOR through
#     AssetPaths.index() (ir_asset.py:396), called from _process_path (ir_asset.py:229) on every
#     _get_asset_paths() run (ir_asset.py:129) - a renamed/removed anchor makes it raise
#     ValueError("File(s) ... not found in bundle ...") (ir_asset.py:431, _raise_not_found);
#   * a ('remove', path) directive resolves through the SAME `_raise_not_found` from
#     AssetPaths.remove() (ir_asset.py:420-429) when the path being removed is not present in the
#     bundle's accumulated path list at that point;
#   * a CONTRIBUTED file that is missing or malformed surfaces only when its own content is
#     fetched: WebAsset._fetch_content (assetsbundle.py:774) raises AssetNotFound on a missing
#     file, which StylesheetAsset._fetch_content (assetsbundle.py:935-958) catches and appends to
#     `bundle.css_errors` instead of raising - a genuine Sass fault lands in that same list.
# None of this is referenced anywhere in odoo/modules/loading.py or odoo/modules/registry.py, so
# -i/-u never triggers it - a module with a dangling anchor or remove target installs clean and
# only explodes the first time a browser actually asks for the bundle. This file is that compile,
# for every bundle in this module's __manifest__.py `assets` key.
#
# This module contributes SCSS ONLY (zero JS anywhere in its assets key), so every bundle below is
# compiled as CSS.
from odoo.tests.common import TransactionCase, tagged

# All three bundles this module's manifest touches. web.assets_backend carries the real
# contribution (an 'after' anchor adding onboarding.scss); web.assets_unit_tests_setup and
# web.tests_assets each carry only a 'remove' directive stripping that same file back out - both
# transitively include web.assets_backend (web/__manifest__.py:454-455, 478-479), so the file is
# present in their accumulated path list before the 'remove' takes it back out.
CSS_BUNDLES = (
    "web.assets_backend",
    "web.assets_unit_tests_setup",
    "web.tests_assets",
)


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):
    """Every asset bundle this module contributes to must actually resolve and compile clean."""

    def test_css_bundles_compile_without_errors(self):
        """web.assets_backend / web.assets_unit_tests_setup / web.tests_assets compile clean.

        WOULD FAIL IF: the `('after', '/onboarding/static/src/scss/onboarding.scss',
        '/viin_brand_onboarding/static/src/scss/onboarding.scss')` anchor this module declares for
        web.assets_backend is orphaned by a future rename of core's own onboarding module SCSS -
        AssetPaths.index() raises ValueError (ir_asset.py:396/431) the moment web.assets_backend is
        resolved; or the `('remove', 'viin_brand_onboarding/static/src/scss/onboarding.scss')`
        entries this module declares for web.assets_unit_tests_setup and web.tests_assets go stale
        (this module's own onboarding.scss renamed without updating those two entries) -
        AssetPaths.remove() raises the same ValueError via _raise_not_found (ir_asset.py:420-429)
        the moment either of those two bundles is resolved; or a genuine Sass fault in this
        module's own onboarding.scss populates `bundle.css_errors` wherever the file is actually
        compiled (web.assets_backend, and transitively the other two before the remove strips it).

        Both `css_errors` and the payload markers are checked - the same two-halves idiom this
        cluster already uses (viin_brand_web/tests/test_bundle_compile.py,
        viin_brand_mail/tests/test_mail_contrast_compile.py) - because `.css()` returns early on an
        already-cached attachment WITHOUT repopulating `css_errors`, so a bundle that failed on an
        EARLIER compile would otherwise read green here while still serving the fallback
        stylesheet (assetsbundle.py:496-511, the literal "## CSS error message ##" /
        "css_error_message" / "A css error occured" markers it bakes into that payload).
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
                self.assertTrue(
                    css.strip(),
                    "%s compiled to empty CSS - the bundle did not build." % bundle_name,
                )
                for marker in ("## CSS error message ##", "css_error_message", "A css error occured"):
                    self.assertNotIn(
                        marker, css,
                        "%s served a CACHED CSS-error fallback payload (marker %r found) - an "
                        "earlier compile failed and the current one only looked clean because "
                        "css() returned the cached attachment without repopulating css_errors."
                        % (bundle_name, marker),
                    )
