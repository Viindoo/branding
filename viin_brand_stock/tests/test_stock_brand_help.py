# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import etree, html

from odoo.tests.common import TransactionCase, tagged

# The Inventory help texts this module owns must not name the Odoo product.
BRAND_TERM = "Odoo"
OPERATION_TYPE_HELP_FIELDS = [
    "use_create_lots",
    "auto_show_allocation_report",
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

    def test_stock_print_section_carries_one_print_note(self):
        arch = self._form_arch()
        stock_notes = self._print_notes(arch, scope="//page[@name='hardware']//")
        self.assertEqual(
            len(stock_notes), 1,
            "the stock Hardware print section must carry exactly one print note",
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


@tagged("post_install", "-at_install")
class TestEmptyStatesNameViindoo(TransactionCase):

    def test_location_and_reordering_rule_empty_states_name_viindoo(self):
        for xmlid in ("stock.action_location_form", "stock.action_orderpoint"):
            with self.subTest(action=xmlid):
                help_text = self.env.ref(xmlid).with_context(lang="en_US").help
                self.assertIn("Viindoo", help_text)

    def test_print_note_says_who_opens_the_preview(self):
        arch = etree.fromstring(self.env["stock.picking.type"].get_view(
            view_id=self.env.ref("stock.view_picking_type_form").id, view_type="form")["arch"].encode("utf-8"))
        notes = arch.xpath("//page[@name='hardware']//div[@colspan='2'][contains(., 'PDF preview')]")
        self.assertEqual(len(notes), 1)
        self.assertIn("Viindoo", " ".join(notes[0].itertext()))


@tagged("post_install", "-at_install")
class TestShippingSettings(TransactionCase):

    def _settings_arch(self):
        view = self.env["res.config.settings"].get_view(view_type="form")
        return etree.fromstring(view["arch"].encode("utf-8"))

    def test_the_button_that_lists_the_shipping_connectors_of_enterprise_is_hidden(self):
        buttons = self._settings_arch().xpath('//setting[@id="delivery"]/button[@type="action"]')
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].get("invisible"), "1")

    def test_the_other_shipping_setting_buttons_stay(self):
        buttons = self._settings_arch().xpath('//setting[@id="delivery"]/button[@type="object"]')
        self.assertTrue(buttons)
        for button in buttons:
            self.assertNotEqual(button.get("invisible"), "1")


@tagged("post_install", "-at_install")
class TestBarcodeDigestTip(TransactionCase):

    def test_the_barcode_tip_names_viindoo_and_loads_its_image_from_this_database(self):
        tip = self.env.ref("stock.digest_tip_stock_0").with_context(lang="en_US")
        text = " ".join(html.fromstring(tip.tip_description).itertext())
        self.assertNotIn(BRAND_TERM, f"{tip.name} {text}")
        self.assertIn("Viindoo", text)
        sources = html.fromstring(tip.tip_description).xpath("//img/@src")
        self.assertTrue(sources)
        for source in sources:
            self.assertTrue(source.startswith("/"), source)
