# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Every bundle this module contributes to must resolve every file it lists and compile with no
# error. Odoo never checks this at install: a bare (untargeted) manifest entry that goes missing
# just drops out of the resolved bundle with no exception (odoo/addons/base/models/ir_asset.py
# `IrAsset._get_paths` falls back to a path with no filename instead of raising), and the failure
# only surfaces once something tries to read that file's content -
# `WebAsset._fetch_content`/`.stat()` (assetsbundle.py:744-786) then raises `AssetNotFound`, which
# a stylesheet asset folds into `bundle.css_errors` (assetsbundle.py:935-958) instead of raising
# out of a bare `.css()` call.
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

    def test_dark_bundle_compiles_the_dashboard_shell_repaint(self):
        """web.assets_web_dark must carry the dashboard shell dark repaint with no Sass fault.

        WOULD FAIL IF: dashboard_action_dark.dark.scss is renamed or deleted (the bare manifest
        entry then resolves with no filename, and fetching its content raises AssetNotFound into
        bundle.css_errors - see the module comment), or the file develops a genuine Sass fault.
        """
        bundle, css = self._compiled_css("web.assets_web_dark")
        self.assertFalse(
            bundle.css_errors,
            "web.assets_web_dark reported SCSS compile errors: %s" % "; ".join(bundle.css_errors),
        )
        self.assertIn(
            "o_spreadsheet_dashboard_search_panel",
            css,
            "web.assets_web_dark compiled without the dashboard shell repaint from "
            "dashboard_action_dark.dark.scss.",
        )
