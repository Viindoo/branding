# -*- coding: utf-8 -*-
import re

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):
    """Every asset bundle this module contributes to resolves and compiles clean.

    Odoo validates neither an asset anchor nor a contributed file at install time, so a dangling
    anchor or a broken SCSS/JS contribution only surfaces when a browser first requests the bundle.
    """

    def test_css_bundles_compile_without_errors(self):
        """web.assets_backend compiles to real, error-free CSS.

        A renamed or removed anchor of this module's ``web._assets_primary_variables`` entry, or a
        Sass fault in any SCSS file it lists under ``web.assets_backend``, fails here.
        """
        # web._assets_primary_variables is not compiled standalone: it does not include
        # web._assets_helpers, so even core's own primary_variables.scss reports an undefined Sass
        # function there. Its anchor is exercised whenever web.assets_backend compiles.
        for bundle_name in ("web.assets_backend",):
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
                # css() returns a cached attachment without repopulating css_errors, so the
                # CSS-error fallback markers are checked in the payload as well.
                for marker in ("## CSS error message ##", "css_error_message", "A css error occured"):
                    self.assertNotIn(
                        marker, css,
                        "%s served a CACHED CSS-error fallback payload (marker %r found) - an "
                        "earlier compile failed and the current one only looked clean because "
                        "css() returned the cached attachment without repopulating css_errors."
                        % (bundle_name, marker),
                    )

    def test_js_bundles_build_with_no_missing_or_malformed_asset(self):
        """web.assets_unit_tests and web.assets_tests resolve every file this module lists and build.

        A missing or syntactically broken JS file of this module fails here.
        """
        # A missing JS file is not raised: it is swallowed into an embedded console.error naming
        # "in file '<path>'". Matching that wrapping on this module's own path avoids false hits on
        # core files whose test content legitimately contains phrases such as "does not exist".
        missing_own_asset_re = re.compile(r"in file 'viin_backend_theme/[^']*'")
        for bundle_name in ("web.assets_unit_tests", "web.assets_tests"):
            with self.subTest(bundle=bundle_name):
                bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=False, js=True)
                js_attachment = bundle.js()
                self.assertTrue(
                    js_attachment,
                    "%s did not produce a JS attachment - the bundle did not build." % bundle_name,
                )
                js = (js_attachment.raw or b"").decode("utf-8", "replace")
                match = missing_own_asset_re.search(js)
                self.assertIsNone(
                    match,
                    "%s compiled with a swallowed missing-asset error for one of this module's "
                    "own files (matched %r) - that file is missing on disk."
                    % (bundle_name, match.group(0) if match else None),
                )
