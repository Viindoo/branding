# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree

from odoo.tests.common import HttpCase, TransactionCase, tagged
from odoo.tools import file_open

from .common import activate_frontend_lang

BRAND_TERM = "Odoo"
QR_CODE_FIELD = "point_of_sale_use_ticket_qr_code"
# the customer display page has its own bundle, apart from point_of_sale._assets_pos
CUSTOMER_DISPLAY_BUNDLE = "point_of_sale.customer_display_assets"
LOGO_OVERRIDE = "viin_brand_pos/static/src/app/components/odoo_logo/odoo_logo.xml"
CORE_LOGO = "point_of_sale/static/src/app/components/odoo_logo/odoo_logo.xml"
IOT_NOTICE_PATCH = "viin_brand_pos/static/src/customer_display/customer_display_data_service.js"
IOT_NOTICE_WRAPPER = "viin_brand_pos/static/src/customer_display/iot_notice.js"


@tagged("post_install", "-at_install")
class TestPosBrandHelp(TransactionCase):

    def test_self_service_invoicing_field_help_does_not_name_odoo(self):
        help_text = self.env["res.company"].fields_get([QR_CODE_FIELD], attributes=["help"])[QR_CODE_FIELD]["help"]
        self.assertTrue(help_text, "the receipt QR code option must keep an explanatory help")
        self.assertNotIn(BRAND_TERM, help_text, "the help of the receipt QR code option must not name Odoo")

    def test_self_service_invoicing_setting_help_does_not_name_odoo(self):
        view = self.env["res.config.settings"].get_view(
            view_id=self.env.ref("point_of_sale.res_config_settings_view_form").id, view_type="form")
        arch = etree.fromstring(view["arch"].encode("utf-8"))
        settings = arch.xpath("//setting[field[@name='%s']]" % QR_CODE_FIELD)
        self.assertEqual(len(settings), 1, "the receipt QR code setting must be on the POS settings form")
        self.assertTrue(settings[0].get("help"), "the receipt QR code setting must keep its help")
        self.assertNotIn(BRAND_TERM, settings[0].get("help"), "the help of the receipt QR code setting must not name Odoo")


@tagged("post_install", "-at_install")
class TestCustomerDisplayTranslations(HttpCase):

    def test_customer_display_page_receives_this_module_translations(self):
        activate_frontend_lang(self.env, "vi_VN")
        modules = self.url_open("/website/translations?lang=vi_VN").json()["modules"]
        self.assertTrue(modules.get("viin_brand_pos", {}).get("messages"), "this module's terms must be served")
        self.assertIn("point_of_sale", modules, "the translations core already sends must be kept")


@tagged("post_install", "-at_install")
class TestCustomerDisplayAssets(TransactionCase):

    def _paths(self, bundle):
        return [path for path, _full, _bundle, _mtime in
                self.env["ir.asset"]._get_asset_paths(bundle=bundle, assets_params={})]

    def test_customer_display_bundle_swaps_the_logo_template_after_core(self):
        paths = [p.lstrip("/") for p in self._paths(CUSTOMER_DISPLAY_BUNDLE)]
        self.assertIn(CORE_LOGO, paths, "core must keep providing point_of_sale.OdooLogo on the customer display")
        self.assertIn(LOGO_OVERRIDE, paths, "the Viindoo logo extension must reach the customer display bundle")
        self.assertGreater(
            paths.index(LOGO_OVERRIDE), paths.index(CORE_LOGO),
            "the extension must come after the template it extends",
        )

    def test_customer_display_bundle_carries_the_iot_notice_replacement(self):
        paths = [p.lstrip("/") for p in self._paths(CUSTOMER_DISPLAY_BUNDLE)]
        self.assertIn(IOT_NOTICE_PATCH, paths)
        self.assertIn(IOT_NOTICE_WRAPPER, paths, "the patch imports the wrapper: it must ship in the same bundle")

    def test_core_customer_display_still_emits_the_message_the_notice_patch_replaces(self):
        # The IoT notice swap matches core's message by equality, so it silently stops working
        # the day core rewords it: this is the drift alarm.
        core_message = ("Make sure there is an IoT Box subscription associated with your Odoo "
                        "database, then restart the IoT Box.")
        with file_open("point_of_sale/static/src/customer_display/customer_display_data_service.js") as f:
            self.assertIn(core_message, f.read())


@tagged("post_install", "-at_install")
class TestPosBundlesDebrandCoreWording(TransactionCase):
    """The POS bundles never include web.assets_backend: the de-brand files must be listed in them."""

    BRAND_FILES = [
        "viin_brand_web/static/src/core/errors/error_dialogs.js",
        "viin_brand_web/static/src/core/errors/error_dialogs.xml",
        "viin_brand_pos/static/src/app/errors/error_dialogs.js",
    ]

    def _paths(self, bundle):
        return [path.lstrip("/") for path, _full, _bundle, _mtime in
                self.env["ir.asset"]._get_asset_paths(bundle=bundle, assets_params={})]

    def test_pos_bundle_carries_the_error_dialog_debrand_and_core_wording_patches(self):
        paths = self._paths("point_of_sale._assets_pos")
        for path in self.BRAND_FILES + [
            "viin_brand_pos/static/src/app/screens/product_screen/product_screen.js",
            "viin_brand_pos/static/src/app/services/report_service.js",
        ]:
            with self.subTest(file=path):
                self.assertIn(path, paths)

    def test_customer_display_bundle_carries_the_error_dialog_debrand(self):
        paths = self._paths("point_of_sale.customer_display_assets")
        for path in self.BRAND_FILES:
            with self.subTest(file=path):
                self.assertIn(path, paths)

    def test_backend_bundle_carries_the_printer_checklist_extension(self):
        self.assertIn(
            "viin_brand_pos/static/src/backend/lna_checklist/lna_checklist.xml",
            self._paths("web.assets_backend"),
        )

    def test_sales_details_report_title_fallback_does_not_name_odoo(self):
        arch = self.env.ref("point_of_sale.pos_daily_sales_report_layout")._get_combined_arch()
        titles = arch.xpath("//title")
        self.assertEqual(len(titles), 1)
        self.assertNotIn(BRAND_TERM, etree.tostring(titles[0], encoding="unicode"))
