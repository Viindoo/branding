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

    def test_dark_bundle_compiles_the_dashboard_shell_repaint(self):
        """web.assets_web_dark carries the dashboard shell repaint with no Sass fault.

        A missing SCSS file resolves silently at install and surfaces only as a
        ``bundle.css_errors`` entry when its content is fetched.
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
