# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Every bundle this module contributes to must resolve every file it lists and compile with no
# error. Odoo never checks this at install: a bare (untargeted) manifest entry whose file is
# missing on disk resolves through `IrAsset._get_paths` (ir_asset.py:317-375) to a placeholder
# with NO filename, no exception. The failure only surfaces once something tries to read that
# asset's content: `WebAsset.stat()` (assetsbundle.py:744-751) then falls through to an
# ir.attachment lookup, which also misses and raises `AssetNotFound("Could not find %s" %
# self.name)`; back in `WebAsset._fetch_content` (assetsbundle.py:774-788) that exception is not
# an `IOError`, so it is re-wrapped by the bare `except:` clause into
# `AssetError('Could not get content for %s.' % self.name)`. A stylesheet asset folds that into
# `bundle.css_errors` (assetsbundle.py:935-958). A javascript asset instead routes it through
# `WebAsset.generate_error` (assetsbundle.py:726-729), which ALWAYS wraps the message as
# `f'{msg!r} in file {self.url!r}'` before embedding it in a swallowed `console.error(...)` call
# (`JavascriptAsset.generate_error`, assetsbundle.py:806-808) - a bare phrase like "does not
# exist" is unsafe to grep for: it collides with unrelated core files' own legitimate content
# compiled into the same shared bundle. The one substring every one of these wrapped messages
# carries, and only for the asset that actually failed, is `in file '<that asset's own resolved
# path>'` - so the JS-channel check below is scoped to that asset's own path.
# This module also anchors one file with an `('after', <target>, ...)` directive: that target is
# resolved through `AssetPaths.index()` (ir_asset.py:396), which DOES raise `ValueError("File(s)
# ... not found in bundle ...")` (ir_asset.py:432) the moment the target itself goes missing - a
# failure that surfaces straight out of `_get_asset_bundle()`, before any content is even fetched.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class BundleCompileTest(TransactionCase):
    """Every asset bundle this module contributes to must actually resolve and compile clean."""

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
        """The literal Odoo embeds into a compiled bundle when `asset_path` itself is the asset
        that failed - see the module comment for the exact wrapping chain. Scoping to this
        asset's own resolved path (rather than a bare phrase such as "does not exist") is what
        keeps the check from tripping on unrelated core files' legitimate content compiled into
        the same shared bundle."""
        return "in file '%s'" % asset_path

    def test_dark_bundle_compiles_the_chrome_repaint(self):
        """web.assets_web_dark must carry the spreadsheet chrome dark repaint with no Sass fault.

        WOULD FAIL IF: the `('after', 'spreadsheet/.../o_spreadsheet_variables.scss', ...)` anchor
        target this module inserts after stops existing in the bundle - `_get_asset_bundle()`
        itself raises `ValueError` before any assertion below runs (see the module comment); or
        either contributed SCSS file (spreadsheet_chrome_dark.scss,
        spreadsheet_chrome_dark.dark.scss) is renamed/deleted, which instead surfaces as a
        `bundle.css_errors` entry; or either develops a genuine Sass fault.
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

    def test_tests_bundle_compiles_the_editor_action_tour(self):
        """web.assets_tests must carry the CE spreadsheet-editor test action with no missing file.

        WOULD FAIL IF: test_spreadsheet_editor_action.js is renamed or deleted - the missing file
        is swallowed into an embedded `console.error(...)` string carrying this file's own path
        rather than raised, so a bare "did not raise" would stay green; or a genuine JS syntax
        fault, which does raise uncaught from the ES-module transpile step.
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
            "console.error call - test_spreadsheet_editor_action.js no longer exists on disk.",
        )
        self.assertIn(
            "viin_brand_spreadsheet_chrome_dark_test_editor",
            content,
            "web.assets_tests compiled without the spreadsheet-editor test action from "
            "test_spreadsheet_editor_action.js.",
        )
