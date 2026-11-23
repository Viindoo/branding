# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re
from unittest.mock import patch

from lxml import html

from odoo.tests.common import BaseCase, TransactionCase, tagged
from odoo.tools import file_open
from odoo.tools.binary import BinaryBytes
from odoo.tools.convert import convert_file

from odoo.addons.point_of_sale.models.pos_config import PosConfig
from odoo.addons.viin_brand.tests.test_brand_cascade_compile import _declarations, _iter_rules
from odoo.addons.viin_brand_pos.models.pos_config import CLOSING_PARTNER_NAME, CORE_CLOSING_PARTNER_NAME

BRAND_TERM = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)
ODOO_COLOURS = ("#71639e", "#714b67", "#017e84", "#875a7b", "#00a09d")
PRIMARY_BUTTON_BACKGROUND = "#7f4282"
# the class of the header, also inside a compound such as `.o_pos.pos-topheader`; `.pos-topheader-foo`
# is another class
HEADER_CLASS = re.compile(r"\.pos-topheader(?![\w-])")


def _pos_css(env):
    bundle = env["ir.qweb"]._get_asset_bundle("point_of_sale._assets_pos", css=True, js=False)
    return "".join((attachment.raw or b"").decode("utf-8", "replace") for attachment in bundle.css()).lower()


def _without_unused_core_rules(css):
    """Drop the core rules whose class no template of the POS uses: no element carries them."""
    return re.sub(r"\.button-no-demo\s*\{[^}]*\}", "", css)


def _header_background_declarations(css):
    """Return the background declarations of the compiled rules that style the POS top header itself.

    A module that co-installs with the POS may style the children of the header (a transition on
    ``.pos-topheader > *``), so the rules are read by their subject and their declarations.

    :param str css: the compiled stylesheet
    :return: ``(selector, value)`` for each ``background`` or ``background-color`` declaration
    :rtype: list
    """
    found = []
    for _order, selector, body in _iter_rules(css):
        subject = re.split(r"[\s>+~]+", selector.strip())[-1]
        if HEADER_CLASS.search(subject):
            declarations = _declarations(body, ("background", "background-color"))
            found.extend((selector, value) for value, _important in declarations)
    return found


@tagged("post_install", "-at_install")
class TestPosStyle(TransactionCase):

    def test_pos_stylesheet_leaves_the_header_background_to_core(self):
        css = _pos_css(self.env)
        self.assertTrue(css.strip())
        self.assertEqual(_header_background_declarations(css), [], "the header keeps the background core gives it")

    def test_primary_button_of_the_pos_is_the_viindoo_purple(self):
        rule = re.search(r"(?:^|\})\s*\.btn-primary\b[^{}]*\{([^}]*--btn-bg:[^}]*)\}", _pos_css(self.env))
        self.assertTrue(rule, "the POS stylesheet has no primary button")
        self.assertRegex(rule.group(1), r"--btn-bg:\s*%s\b" % PRIMARY_BUTTON_BACKGROUND)

    def test_pos_stylesheet_carries_no_colour_of_odoo(self):
        css = _without_unused_core_rules(_pos_css(self.env))
        for colour in ODOO_COLOURS:
            with self.subTest(colour=colour):
                self.assertNotIn(colour, css)


@tagged("post_install", "-at_install")
class TestHeaderBackgroundReader(BaseCase):
    """The header guard reads the declarations of the rules that style the header, not a class name."""

    def test_a_background_on_the_header_is_found(self):
        css = ".a{color:red}.pos-topheader{background-color:#7f4282}.o_pos .pos-topheader,.b{background:red}"

        self.assertEqual(
            _header_background_declarations(css),
            [(".pos-topheader", "#7f4282"), (".o_pos .pos-topheader", "red")],
        )

    def test_a_rule_on_the_children_of_the_header_is_not_a_background_of_the_header(self):
        css = ".pos-topheader > *{transition:opacity .2s}.o_fp_edit_mode .pos-topheader > *{opacity:0;background:red}"

        self.assertEqual(_header_background_declarations(css), [])

    def test_a_background_on_the_header_written_as_a_compound_selector_is_found(self):
        css = ".o_pos.pos-topheader{background:red}.pos-navbar.pos-topheader{background-color:blue}"

        self.assertEqual(
            _header_background_declarations(css),
            [(".o_pos.pos-topheader", "red"), (".pos-navbar.pos-topheader", "blue")],
        )

    def test_a_class_that_only_starts_like_the_header_class_is_not_the_header(self):
        self.assertEqual(_header_background_declarations(".pos-topheader-foo{background:red}"), [])

    def test_a_header_rule_without_a_background_is_not_a_background(self):
        self.assertEqual(_header_background_declarations(".pos-topheader{color:red;border:0}"), [])


@tagged("post_install", "-at_install")
class TestPosTexts(TransactionCase):

    def test_receipt_footer_is_powered_by_viindoo(self):
        footer = self.env.ref("point_of_sale.pos_order_receipt_footer")._get_combined_arch()
        text = " ".join(footer.xpath("//div[@name='footer_powered_by']//text()"))
        self.assertNotRegex(text, BRAND_TERM)
        self.assertIn("Viindoo", text)

    def test_price_inclusion_wizard_names_no_odoo(self):
        arch = self.env["pos.price.inclusion.wizard"].get_view(view_type="form")["arch"]
        self.assertNotRegex(" ".join(html.fromstring(arch).xpath("//text()")), BRAND_TERM)

    def test_customer_display_page_title_names_no_odoo(self):
        arch = self.env.ref("point_of_sale.customer_display_index")._get_combined_arch()
        title = arch.xpath("string(//head/title[1])")
        self.assertTrue(title.strip())
        self.assertNotRegex(title, BRAND_TERM)

    def test_pos_page_title_names_no_odoo(self):
        arch = self.env.ref("point_of_sale.index")._get_combined_arch()
        title = arch.xpath("string(//head/title)")
        self.assertTrue(title.strip())
        self.assertNotRegex(title, BRAND_TERM)


@tagged("post_install", "-at_install")
class TestClosingPartner(TransactionCase):

    def test_partner_of_the_closing_entries_names_no_odoo(self):
        partner = self.env.ref("point_of_sale.default_session_closing_partner").with_context(active_test=False)
        self.assertNotRegex(partner.name, BRAND_TERM)

    def _tracking_messages(self, partner):
        return self.env["mail.message"].search([
            ("model", "=", "res.partner"), ("res_id", "=", partner.id), ("message_type", "=", "tracking"),
        ])

    def test_installed_database_has_no_history_line_naming_odoo_on_the_partner(self):
        partner = self.env.ref("point_of_sale.default_session_closing_partner").with_context(active_test=False)
        self.assertFalse(
            self._tracking_messages(partner).filtered(lambda message: BRAND_TERM.search(message.body or "")),
            "the history of the partner of the closing entries must not name Odoo",
        )

    def test_install_leaves_no_history_line_for_the_rename(self):
        partner = self.env.ref("point_of_sale.default_session_closing_partner").with_context(active_test=False)
        self.env["ir.model.data"].search([
            ("module", "=", "point_of_sale"), ("name", "=", "default_session_closing_partner"),
        ]).noupdate = False
        # The partner as core leaves it: named by core, flushed, its tracking window closed.
        partner.with_context(mail_notrack=True).write({"name": CORE_CLOSING_PARTNER_NAME})
        self.env.flush_all()
        self.env.cr.precommit.run()
        known = self._tracking_messages(partner)
        convert_file(self.env, "viin_brand_pos", "data/pos_config_data.xml", None, "init")
        self.env.flush_all()
        self.env.cr.precommit.run()
        self.assertEqual(partner.name, CLOSING_PARTNER_NAME)
        self.assertFalse(
            self._tracking_messages(partner) - known,
            "the branding rename must not show in the history of the partner",
        )

    def test_partner_recreated_for_the_closing_entries_names_no_odoo(self):
        partner = self.env.ref("point_of_sale.default_session_closing_partner").with_context(active_test=False)
        self.env["ir.model.data"].search([
            ("module", "=", "point_of_sale"), ("name", "=", "default_session_closing_partner"),
        ]).unlink()
        partner.unlink()
        config = self.env["pos.config"].create({"name": "Closing shop"})
        recreated = config._get_or_create_default_partner()
        self.assertNotRegex(recreated.name, BRAND_TERM)


@tagged("post_install", "-at_install")
class TestClothesScenario(TransactionCase):

    def _sneakers(self, name="Odoo Sneakers"):
        with file_open("point_of_sale/static/img/product_odoo_sneakers.png", "rb") as image:
            core_image = BinaryBytes(image.read())
        product = self.env["product.product"].create({"name": name, "image_1920": core_image})
        self.env["ir.model.data"].create({
            "module": "point_of_sale",
            "name": "product_odoo_sneakers",
            "model": "product.product",
            "res_id": product.id,
        })
        return product, product.image_1920

    def test_loading_the_clothes_scenario_gives_the_sneakers_a_neutral_name_and_image(self):
        product, core_image = self._sneakers()
        config = self.env["pos.config"].create({"name": "Shop of the test"})
        with patch.object(PosConfig, "_load_onboarding_clothes_demo_data", return_value=None):
            config._load_onboarding_clothes_demo_data()
        self.assertEqual(product.name, "Sneakers")
        self.assertTrue(product.image_1920)
        self.assertNotEqual(product.image_1920, core_image)

    def test_installing_the_module_renames_sneakers_a_demo_database_already_holds(self):
        product, core_image = self._sneakers()
        self.env["pos.config"]._debrand_clothes_scenario()
        self.assertEqual(product.name, "Sneakers")
        self.assertNotEqual(product.image_1920, core_image)

    def test_sneakers_the_user_renamed_are_left_as_they_are(self):
        product, core_image = self._sneakers(name="My own sneakers")
        self.env["pos.config"]._debrand_clothes_scenario()
        self.assertEqual(product.name, "My own sneakers")
        self.assertEqual(product.image_1920, core_image)
