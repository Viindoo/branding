# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree, html

from odoo.tests.common import TransactionCase, tagged

BRAND_TERM = "Odoo"
QR_CODE_FIELD = "point_of_sale_use_ticket_qr_code"
# the customer display page has its own bundle, apart from point_of_sale._assets_pos
CUSTOMER_DISPLAY_BUNDLE = "point_of_sale.customer_display_assets"
LOGO_OVERRIDE = "viin_brand_pos/static/src/app/components/odoo_logo/odoo_logo.xml"
CORE_LOGO = "point_of_sale/static/src/app/components/odoo_logo/odoo_logo.xml"
DISPLAY_OVERRIDE = "viin_brand_pos/static/src/customer_display/customer_display.xml"
CORE_DISPLAY = "point_of_sale/static/src/customer_display/customer_display.xml"


@tagged("post_install", "-at_install")
class TestPosBrandHelp(TransactionCase):

    def test_self_service_invoicing_field_help_does_not_name_odoo(self):
        help_text = self.env["res.company"].fields_get([QR_CODE_FIELD], attributes=["help"])[QR_CODE_FIELD]["help"]
        self.assertTrue(help_text, "the receipt QR code option must keep an explanatory help")
        self.assertNotIn(BRAND_TERM, help_text, "the help of the receipt QR code option must not name Odoo")
        self.assertIn("Viindoo", help_text)

    def test_self_service_invoicing_setting_help_does_not_name_odoo(self):
        view = self.env["res.config.settings"].get_view(
            view_id=self.env.ref("point_of_sale.res_config_settings_view_form").id, view_type="form")
        arch = etree.fromstring(view["arch"].encode("utf-8"))
        settings = arch.xpath("//setting[field[@name='%s']]" % QR_CODE_FIELD)
        self.assertEqual(len(settings), 1, "the receipt QR code setting must be on the POS settings form")
        self.assertTrue(settings[0].get("help"), "the receipt QR code setting must keep its help")
        self.assertNotIn(BRAND_TERM, settings[0].get("help"), "the help of the receipt QR code setting must not name Odoo")
        self.assertIn("Viindoo", settings[0].get("help"))


@tagged("post_install", "-at_install")
class TestCustomerDisplayAssets(TransactionCase):

    def _paths(self, bundle):
        return [path.lstrip("/") for path, _full, _bundle, _mtime in
                self.env["ir.asset"]._get_asset_paths(bundle=bundle, assets_params={})]

    def test_customer_display_bundle_swaps_the_logo_template_after_core(self):
        paths = self._paths(CUSTOMER_DISPLAY_BUNDLE)
        self.assertIn(CORE_LOGO, paths, "core must keep providing point_of_sale.OdooLogo on the customer display")
        self.assertIn(LOGO_OVERRIDE, paths, "the Viindoo logo extension must reach the customer display bundle")
        self.assertGreater(
            paths.index(LOGO_OVERRIDE), paths.index(CORE_LOGO),
            "the extension must come after the template it extends",
        )

    def test_customer_display_bundle_extends_the_idle_screen_after_core(self):
        paths = self._paths(CUSTOMER_DISPLAY_BUNDLE)
        self.assertIn(DISPLAY_OVERRIDE, paths, "the idle screen logo extension must reach the customer display")
        self.assertGreater(paths.index(DISPLAY_OVERRIDE), paths.index(CORE_DISPLAY))


@tagged("post_install", "-at_install")
class TestPosBundlesDebrandCoreWording(TransactionCase):
    """The POS bundles never include web.assets_backend: the de-brand files must be listed in them."""

    BRAND_FILES = [
        "viin_brand/static/src/core/dialog/dialog.js",
        "viin_brand/static/src/core/errors/error_dialogs.js",
        "viin_brand/static/src/core/errors/error_dialogs.xml",
    ]

    def _paths(self, bundle):
        return [path.lstrip("/") for path, _full, _bundle, _mtime in
                self.env["ir.asset"]._get_asset_paths(bundle=bundle, assets_params={})]

    def test_pos_bundle_carries_the_error_dialog_debrand_and_core_wording_patches(self):
        paths = self._paths("point_of_sale._assets_pos")
        for path in self.BRAND_FILES + [
            "viin_brand/static/src/core/barcode/barcode_video_scanner.js",
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

    def _report_title(self, **values):
        layout = self.env["ir.qweb"]._render("point_of_sale.pos_daily_sales_report_layout", values)
        return html.fromstring(str(layout)).findtext(".//head/title")

    def test_sales_details_report_title_is_the_title_of_the_report_else_names_no_odoo(self):
        self.assertEqual(self._report_title(title="Sales of the day"), "Sales of the day")
        self.assertNotIn(BRAND_TERM, self._report_title())
