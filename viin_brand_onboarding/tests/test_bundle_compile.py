from odoo.tests.common import TransactionCase, tagged

# web.assets_backend carries the contribution; the two test bundles include it and strip it back out.
CSS_BUNDLES = (
    "web.assets_backend",
    "web.assets_unit_tests_setup",
    "web.tests_assets",
)


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):

    def test_css_bundles_compile_without_errors(self):
        """Every asset anchor and SCSS contribution of this module resolves and compiles cleanly.

        Odoo validates neither at install time: a dangling ``after`` anchor or ``remove`` target
        raises only when the bundle is resolved, and a Sass fault lands in ``bundle.css_errors``.
        Both ``css_errors`` and the fallback payload markers are checked, because ``css()`` returns
        a cached attachment without repopulating ``css_errors``.
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
                        "%s served a cached CSS-error fallback payload (marker %r found)."
                        % (bundle_name, marker),
                    )
