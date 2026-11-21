# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re

from lxml import etree

from odoo.addons.viin_brand_mail.tests.test_discuss_chrome_compile import _last_declared_in
from odoo.addons.viin_brand_mail.tests.test_mail_contrast_compile import (
    ANY_ANCESTORS,
    BACKEND_BUNDLE,
    DARK_BUNDLE,
    ContrastCompileHelpers,
    _bodies_matching,
    _custom_property_re,
    _declared_values,
)
from odoo.modules import Manifest
from odoo.tests.common import TransactionCase, tagged

_COLOR_RE = re.compile(r"(?<![\w-])color\s*:\s*([^;]+)", re.IGNORECASE)
HELP_LABEL = ".o-livechat-LivechatStatusLabel.o-help"
HEADER_LABEL = ".o-mail-ChatWindow-header .o-livechat-LivechatStatusLabel"


@tagged("post_install", "-at_install")
class TestLivechatChromeCompile(ContrastCompileHelpers, TransactionCase):

    def test_status_label_in_the_chat_window_header_is_white_in_both_schemes(self):
        for bundle in (BACKEND_BUNDLE, DARK_BUNDLE):
            with self.subTest(bundle=bundle):
                css = self._compiled_css(bundle)
                self.assertIn(
                    _last_declared_in(self, css, HEADER_LABEL, _COLOR_RE),
                    ("#fff", "#ffffff", "white"),
                )

    def test_need_help_label_outside_the_header_is_the_viindoo_purple(self):
        css = self._compiled_css(BACKEND_BUNDLE)
        self.assertIn("#7f4282", _last_declared_in(self, css, HELP_LABEL, _COLOR_RE))
        dark_css = self._compiled_css(DARK_BUNDLE)
        bodies = _bodies_matching(dark_css, lambda token: token == HELP_LABEL, ANY_ANCESTORS)
        values = _declared_values(bodies, _custom_property_re("livechat-LivechatStatusLabel-helpColor"))
        self.assertEqual(values[-1], "#bd83c0")


@tagged("post_install", "-at_install")
class TestLivechatBundlesAndViews(TransactionCase):

    def _paths(self, bundle):
        return [
            path.lstrip("/")
            for path, _full, _bundle, _mtime in self.env["ir.asset"]._get_asset_paths(
                bundle=bundle, assets_params={}
            )
        ]

    def test_embed_bundles_carry_the_dialog_files_and_the_client_patches(self):
        external = self._paths("im_livechat.assets_embed_external")
        for path in (
            "viin_brand/static/src/core/dialog/dialog.js",
            "viin_brand/static/src/core/errors/error_dialogs.js",
            "viin_brand/static/src/core/errors/error_dialogs.xml",
            "viin_brand_mail/static/src/core/common/notification_permission_service.js",
            "viin_brand_mail/static/src/core/common/out_of_focus_service.js",
        ):
            with self.subTest(file=path):
                self.assertIn(path, external)

    def test_frontend_title_patch_is_listed_only_where_the_core_title_service_is(self):
        paths = self._paths("web.assets_frontend")
        core = "web/static/src/core/browser/title_service.js" in paths
        brand = "viin_brand/static/src/core/browser/title_service.js" in paths
        self.assertEqual(
            brand, core,
            "the viin_brand title patch must not be served without the core title service it patches",
        )

    def test_agents_hint_names_viindoo(self):
        arch = self.env["im_livechat.channel"].get_views([[False, "form"]])["views"]["form"]["arch"]
        paragraphs = etree.fromstring(arch).xpath("//page[@name='Agents']//p[contains(@class, 'text-muted')]")
        texts = " ".join(text for paragraph in paragraphs for text in paragraph.xpath(".//text()"))
        self.assertIn("Agents who are inactive in Viindoo for more than 30 minutes", texts)
        self.assertNotIn("in the system", texts)
        self.assertNotIn("Odoo", texts)

    def _assert_support_page_powered_by_viindoo(self, arch):
        strongs = arch.xpath("//body/div[hasclass('main')]/div/strong")
        self.assertEqual([strong.text for strong in strongs], ["Viindoo"])
        self.assertFalse(strongs[0].get("style"), "the name is shown, not hidden")
        self.assertNotIn("Odoo", " ".join(arch.xpath("//body//text()")))

    def test_support_page_is_powered_by_viindoo_without_a_hidden_odoo(self):
        arch = self.env.ref("im_livechat.support_page")._get_combined_arch()
        self._assert_support_page_powered_by_viindoo(arch)


@tagged("post_install", "-at_install")
class TestLivechatDependencies(TransactionCase):

    def test_depends_names_viin_brand_whose_files_the_module_references(self):
        manifest = Manifest.for_addon("viin_brand_im_livechat", display_warning=False)
        self.assertIn("viin_brand", manifest["depends"])
