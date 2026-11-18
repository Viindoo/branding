# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):
    def _compiled_css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        return bundle, css

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

    def test_dark_bundle_compiles_the_chrome_repaint(self):
        """web.assets_web_dark carries the chrome repaint and the chatter island rules, with no Sass fault.

        A dangling ``after`` anchor raises ``ValueError`` from ``_get_asset_bundle()``; a missing
        or malformed SCSS file lands in ``bundle.css_errors``.
        """
        bundle, css = self._compiled_css("web.assets_web_dark")
        self.assertFalse(
            bundle.css_errors,
            "web.assets_web_dark reported SCSS compile errors: %s" % "; ".join(bundle.css_errors),
        )
        self.assertIn(
            "o-spreadsheet-topbar-wrapper",
            css,
            "web.assets_web_dark compiled without the chrome repaint from "
            "spreadsheet_chrome_dark.dark.scss.",
        )
        self.assertIn(
            ".o-spreadsheet .o-mail-Chatter",
            css,
            "web.assets_web_dark compiled without the island rules of "
            "spreadsheet_chatter_island.dark.scss.",
        )

    def test_tests_bundle_compiles_the_editor_action_tour(self):
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
            "viin_brand_spreadsheet_chrome_dark_test_editor",
            content,
            "web.assets_tests compiled without the spreadsheet-editor test action from "
            "test_spreadsheet_editor_action.js.",
        )
