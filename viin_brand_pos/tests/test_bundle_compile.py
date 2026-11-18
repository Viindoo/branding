# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Every asset bundle this module contributes to compiles clean.

Odoo validates a bundle lazily, the first time a browser asks for it, never at module install: a
renamed anchor of an ``after`` directive raises when the asset paths are resolved, a missing
literal path is embedded in the compiled bundle as a swallowed ``console.error``, a missing or
malformed XML template as a ``throw new Error``, and a Sass fault lands in ``bundle.css_errors``.
A glob entry silently drops a deleted file and a plain ``.css`` file is never Sass-validated, so
neither is caught here.
"""
import re

from odoo.tests.common import TransactionCase, tagged


def _own_swallowed_asset_errors(js_text):
    """Return every swallowed-error call in ``js_text`` naming one of this module's own paths.

    Core code freely uses ``console.error(...)`` and ``throw new Error(...)`` with its own
    messages, so only a call that names a ``viin_brand_pos/`` path is a missing asset of this
    module: the failing asset's own url is baked into the wrapped message.
    """
    swallowed_call = re.compile(r'(?:console\.error|throw new Error)\("(?:[^"\\]|\\.)*"\)')
    return [call for call in swallowed_call.findall(js_text) if "viin_brand_pos/" in call]


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):
    """Every bundle this module contributes to must actually resolve and compile clean."""

    def test_css_bundles_compile_without_errors(self):
        """The POS bundles compile to real, error-free CSS."""
        for bundle_name in ("point_of_sale._assets_pos", "point_of_sale.assets_prod"):
            with self.subTest(bundle=bundle_name):
                bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
                attachments = bundle.css() or self.env["ir.attachment"]
                css = "".join(
                    (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
                )
                self.assertFalse(
                    bundle.css_errors,
                    "%s reported SCSS/CSS compile errors: %s" % (bundle_name, "; ".join(bundle.css_errors)),
                )
                self.assertTrue(
                    css.strip(),
                    "%s compiled to empty CSS - the bundle did not build." % bundle_name,
                )
                # css() returns a cached error stylesheet of an earlier failed compile without
                # repopulating css_errors
                for marker in ("## CSS error message ##", "css_error_message", "A css error occured"):
                    self.assertNotIn(
                        marker, css,
                        "%s served a cached CSS-error fallback payload (marker %r found)"
                        % (bundle_name, marker),
                    )

    def test_js_bundles_build_with_no_missing_or_malformed_asset(self):
        """The bundles carrying this module's JS and templates build with no missing or malformed asset."""
        for bundle_name in (
            "point_of_sale._assets_pos",
            "point_of_sale.customer_display_assets",
            "web.assets_tests",
            "web.assets_unit_tests",
        ):
            with self.subTest(bundle=bundle_name):
                bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=False, js=True)
                js_attachment = bundle.js()
                self.assertTrue(
                    js_attachment,
                    "%s did not produce a JS attachment - the bundle did not build." % bundle_name,
                )
                js = (js_attachment.raw or b"").decode("utf-8", "replace")
                own_errors = _own_swallowed_asset_errors(js)
                self.assertFalse(
                    own_errors,
                    "%s compiled with a swallowed error naming one of viin_brand_pos's own asset "
                    "paths (a missing JS file, or a missing/malformed XML template): %s"
                    % (bundle_name, own_errors),
                )
