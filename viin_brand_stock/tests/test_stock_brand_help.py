# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree

from odoo.tests.common import TransactionCase, tagged

# The Inventory help texts this module owns must not name the Odoo product.
BRAND_TERM = "Odoo"
PDF_PREVIEW_FRAGMENT = "PDF preview"
OPERATION_TYPE_HELP_FIELDS = [
    "use_create_lots",
    "auto_show_reception_report",
    "auto_print_delivery_slip",
    "auto_print_return_slip",
    "auto_print_product_labels",
    "auto_print_lot_labels",
    "auto_print_reception_report",
    "auto_print_reception_report_labels",
    "auto_print_packages",
    "auto_print_package_label",
]
ORDERPOINT_QTY_FIELDS = ["product_min_qty", "product_max_qty"]


@tagged("post_install", "-at_install")
class TestPickingTypeFormNote(TransactionCase):

    def _form_arch(self):
        view = self.env["stock.picking.type"].get_view(
            view_id=self.env.ref("stock.view_picking_type_form").id, view_type="form")
        return etree.fromstring(view["arch"].encode("utf-8"))

    def _print_notes(self, arch, scope="//"):
        return arch.xpath(
            scope + "div[@colspan='2'][contains(., 'PDF preview') or widget[@name='documentation_link']]")

    def test_operation_type_form_has_no_documentation_link_widget(self):
        arch = self._form_arch()
        self.assertFalse(
            arch.xpath("//widget[@name='documentation_link']"),
            "the Operation Type form must not keep the Odoo documentation link",
        )

    def test_operation_type_form_print_notes_do_not_name_odoo(self):
        arch = self._form_arch()
        notes = self._print_notes(arch)
        self.assertTrue(notes, "the Operation Type form must keep a print note")
        for note in notes:
            with self.subTest(note=" ".join(note.itertext()).split()[:4]):
                self.assertNotIn(
                    BRAND_TERM, " ".join(note.itertext()),
                    "a print note on the Operation Type form must not name Odoo",
                )

    def test_stock_print_section_note_shows_pdf_preview(self):
        arch = self._form_arch()
        stock_notes = self._print_notes(arch, scope="//page[@name='hardware']//")
        self.assertEqual(
            len(stock_notes), 1,
            "the stock Hardware print section must carry exactly one print note",
        )
        self.assertIn(
            PDF_PREVIEW_FRAGMENT, " ".join(stock_notes[0].itertext()),
            "the stock print note must say that a PDF preview opens by default",
        )


@tagged("post_install", "-at_install")
class TestPickingTypeHelp(TransactionCase):

    def test_operation_type_help_texts_do_not_name_odoo(self):
        field_info = self.env["stock.picking.type"].fields_get(OPERATION_TYPE_HELP_FIELDS, attributes=["help"])
        for name in OPERATION_TYPE_HELP_FIELDS:
            with self.subTest(field=name):
                self.assertNotIn(
                    BRAND_TERM, field_info[name]["help"],
                    "the help of an Operation Type auto-print option must not name Odoo",
                )


@tagged("post_install", "-at_install")
class TestPickingLotCreationHelp(TransactionCase):

    def test_lot_creation_help_on_transfer_and_move_line_does_not_name_odoo(self):
        for model, name in [("stock.picking", "use_create_lots"),
                            ("stock.move.line", "picking_type_use_create_lots")]:
            with self.subTest(model=model, field=name):
                help_text = self.env[model].fields_get([name], attributes=["help"])[name]["help"]
                self.assertNotIn(
                    BRAND_TERM, help_text,
                    "the lot-creation help on a Transfer or move line must not name Odoo",
                )


@tagged("post_install", "-at_install")
class TestOrderpointQuantityHelp(TransactionCase):

    def test_min_max_quantity_help_does_not_name_odoo(self):
        field_info = self.env["stock.warehouse.orderpoint"].fields_get(
            ORDERPOINT_QTY_FIELDS, attributes=["help"])
        for name in ORDERPOINT_QTY_FIELDS:
            with self.subTest(field=name):
                self.assertNotIn(
                    BRAND_TERM, field_info[name]["help"],
                    "the help of a reordering rule Min/Max quantity must not name Odoo",
                )
