# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree

from odoo.tests.common import TransactionCase, tagged

# The Manufacturing help texts this module owns must not name the Odoo product.
BRAND_TERM = "Odoo"
PDF_PREVIEW_FRAGMENT = "PDF preview"
AUTO_PRINT_FIELDS = [
    "auto_print_done_production_order",
    "auto_print_done_mrp_product_labels",
    "auto_print_done_mrp_lot",
    "auto_print_mrp_reception_report",
    "auto_print_mrp_reception_report_labels",
]


@tagged("post_install", "-at_install")
class TestMrpBomOperationDependenciesHelp(TransactionCase):

    def test_operation_dependencies_help_does_not_name_odoo(self):
        help_text = self.env["mrp.bom"].fields_get(
            ["allow_operation_dependencies"], attributes=["help"]
        )["allow_operation_dependencies"]["help"]
        self.assertNotIn(
            BRAND_TERM, help_text,
            "the Operation Dependencies help on the BoM must not name Odoo",
        )


@tagged("post_install", "-at_install")
class TestStockMoveManualConsumptionHelp(TransactionCase):

    def test_manual_consumption_help_does_not_name_odoo(self):
        help_text = self.env["stock.move"].fields_get(
            ["manual_consumption"], attributes=["help"]
        )["manual_consumption"]["help"]
        self.assertNotIn(
            BRAND_TERM, help_text,
            "the Manual Consumption help on the stock move must not name Odoo",
        )


@tagged("post_install", "-at_install")
class TestPickingTypeAutoPrintHelp(TransactionCase):

    def test_manufacturing_auto_print_help_does_not_name_odoo(self):
        field_info = self.env["stock.picking.type"].fields_get(
            AUTO_PRINT_FIELDS, attributes=["help"])
        for name in AUTO_PRINT_FIELDS:
            with self.subTest(field=name):
                self.assertNotIn(
                    BRAND_TERM, field_info[name]["help"],
                    "the help of a Manufacturing auto-print option must not name Odoo",
                )


@tagged("post_install", "-at_install")
class TestPickingTypeMrpPrintNote(TransactionCase):

    def _mrp_hardware_page(self):
        view = self.env["stock.picking.type"].get_view(
            view_id=self.env.ref("stock.view_picking_type_form").id, view_type="form")
        arch = etree.fromstring(view["arch"].encode("utf-8"))
        pages = arch.xpath("//page[@name='mrp_hardware']")
        self.assertEqual(
            len(pages), 1,
            "the Operation Type form must carry the Manufacturing Hardware page",
        )
        return pages[0]

    def test_mrp_print_note_has_no_documentation_link_widget(self):
        page = self._mrp_hardware_page()
        self.assertFalse(
            page.xpath(".//widget[@name='documentation_link']"),
            "the Manufacturing print note on the Operation Type form must not keep the Odoo documentation link",
        )

    def test_mrp_print_note_says_pdf_preview_without_odoo(self):
        page = self._mrp_hardware_page()
        notes = page.xpath(f".//div[@colspan='2'][contains(., '{PDF_PREVIEW_FRAGMENT}')]")
        self.assertEqual(
            len(notes), 1,
            "the Manufacturing Hardware page must carry exactly one PDF preview note",
        )
        self.assertNotIn(
            BRAND_TERM, " ".join(notes[0].itertext()),
            "the Manufacturing print note on the Operation Type form must not name Odoo",
        )
