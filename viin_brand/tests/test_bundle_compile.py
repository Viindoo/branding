# Copyright 2026 Viindoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestBrandBundleCompile(TransactionCase):
    """Every bundle this module contributes to must actually carry this module's files.

    A manifest asset entry with no `after`/`before`/`replace` target - which is every entry this
    module declares - resolves through a plain filesystem glob with no existence check: a renamed
    or deleted file just drops out of the resolved list, no exception raised, and the bundle still
    "compiles" successfully without it. Only compiling the real bundle and checking this module's
    own content actually landed in it - not merely that some (other module's) content did -
    proves the wiring.
    """

    def _compiled_js(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(
            bundle_name, css=False, js=True, debug_assets=True,
        )
        attachment = bundle.js()
        return (attachment.raw or b"").decode("utf-8", "replace")

    def test_backend_bundle_carries_the_webclient_favicon_patch(self):
        content = self._compiled_js("web.assets_backend")
        self.assertIn(
            "/web/image/res.company/",
            content,
            "web.assets_backend compiled without the favicon patch from "
            "viin_brand/static/src/webclient/webclient.js.",
        )

    def test_backend_bundle_carries_the_settings_page_icon_patch(self):
        content = self._compiled_js("web.assets_backend")
        self.assertIn(
            "get_viin_brand_modules_icon",
            content,
            "web.assets_backend compiled without the module-icon RPC from "
            "viin_brand/static/src/js/settings_page.js.",
        )

    def test_backend_bundle_carries_the_settings_page_template_extension(self):
        content = self._compiled_js("web.assets_backend")
        self.assertIn(
            'registerTemplateExtension("web.SettingsPage"',
            content,
            "web.assets_backend compiled without the web.SettingsPage extension from "
            "viin_brand/static/src/xml/settings_page.xml.",
        )

    def test_tests_assets_bundle_carries_the_mock_server_icon_stub(self):
        content = self._compiled_js("web.tests_assets")
        self.assertIn(
            "viin_brand/static/img/apps/settings.png",
            content,
            "web.tests_assets compiled without the mocked icon response from "
            "viin_brand/static/tests/viin_brand_mock_server.js.",
        )
