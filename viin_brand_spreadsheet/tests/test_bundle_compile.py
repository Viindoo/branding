# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import os
import re

from odoo.modules import get_module_path
from odoo.tests.common import TransactionCase, tagged

TOKEN_BUNDLES = ("web.assets_backend", "spreadsheet.public_spreadsheet")
TOKEN_DECLARATION = re.compile(r"--os-primary-button-bg\s*:\s*([^;]+);")
TOKENS_CSS = os.path.join("static", "src", "css", "spreadsheet_tokens.css")


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):
    def _compiled_css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        return bundle, css

    def _shipped_declaration(self):
        """The value the module's own stylesheet gives the primary button token."""
        path = os.path.join(get_module_path("viin_brand_spreadsheet"), TOKENS_CSS)
        with open(path, "r", encoding="utf-8") as handle:
            declarations = TOKEN_DECLARATION.findall(handle.read())
        self.assertEqual(len(declarations), 1, "the palette block declares the token once")
        return re.sub(r"\s+", "", declarations[0]).lower()

    def _compiled_js(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=False, js=True)
        js_attachment = bundle.js()
        content = (js_attachment.raw or b"").decode("utf-8", "replace") if js_attachment else ""
        return js_attachment, content

    def _own_asset_error_marker(self, asset_path):
        """Return the text Odoo embeds in a compiled bundle when ``asset_path`` itself failed.

        A bare phrase such as "does not exist" would also match unrelated core files compiled into
        the same shared bundle, so the marker is scoped to the asset's own resolved path.
        """
        return "in file '%s'" % asset_path

    def test_the_palette_block_lands_after_the_engine_stylesheet_in_every_bundle_that_has_it(self):
        """The block wins over the engine's own declaration only by coming after it."""
        for bundle_name in TOKEN_BUNDLES:
            with self.subTest(bundle=bundle_name):
                bundle, css = self._compiled_css(bundle_name)
                self.assertFalse(
                    bundle.css_errors,
                    "%s reported CSS compile errors: %s" % (bundle_name, "; ".join(bundle.css_errors)),
                )
                declarations = [
                    re.sub(r"\s+", "", value).lower() for value in TOKEN_DECLARATION.findall(css)
                ]
                self.assertGreaterEqual(
                    len(declarations), 2,
                    "%s holds the primary button token only %d time(s): the engine's declaration "
                    "and the brand block must both be there." % (bundle_name, len(declarations)),
                )
                self.assertEqual(declarations[-1], self._shipped_declaration())

    def test_tests_bundle_compiles_the_editor_action(self):
        """web.assets_tests carries the CE spreadsheet-editor test action with no missing file.

        A missing file is swallowed into an embedded ``console.error(...)`` string carrying its own
        path rather than raised, so the absence of that marker is asserted.
        """
        js_attachment, content = self._compiled_js("web.assets_tests")
        self.assertTrue(
            js_attachment,
            "web.assets_tests did not produce a JS attachment - the bundle did not build.",
        )
        self.assertNotIn(
            self._own_asset_error_marker(
                "viin_brand_spreadsheet/static/tests/tours/test_spreadsheet_editor_action.js"
            ),
            content,
            "web.assets_tests compiled with a swallowed missing-asset error embedded as a "
            "console.error call - test_spreadsheet_editor_action.js does not exist on disk.",
        )
        self.assertIn(
            "viin_brand_spreadsheet_palette_test_editor",
            content,
            "web.assets_tests compiled without the spreadsheet-editor test action from "
            "test_spreadsheet_editor_action.js.",
        )
