import os
import re

from lxml import etree

from odoo.modules.module import get_manifest, get_module_path
from odoo.tests.common import TransactionCase, tagged

PRODUCT_NAME = re.compile(r'\bOdoo\b|odoo\.com', re.IGNORECASE)
MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (this module's template extension, core file that inserts the node the extension removes)
POS_TEMPLATE_EXTENSIONS = [
    (
        'static/src/overrides/screens/floor_screen/floor_screen.xml',
        'static/src/overrides/screens/floor_screen/floor_screen.xml',
    ),
    (
        'static/src/overrides/components/navbar/navbar.xml',
        'static/src/overrides/components/navbar/navbar.xml',
    ),
]


@tagged('post_install', '-at_install')
class TestSelfOrderBrandSurfaces(TransactionCase):

    def test_custom_link_list_placeholders_are_neutral_samples(self):
        arch = etree.fromstring(self.env['pos_self_order.custom_link'].get_view(
            view_id=self.env.ref('pos_self_order.custom_link_tree').id, view_type='list')['arch'])
        for name in ('name', 'url'):
            field = arch.xpath('//field[@name="%s"]' % name)
            self.assertEqual(len(field), 1, name)
            self.assertTrue(field[0].get('placeholder'), name)
            self.assertNotRegex(field[0].get('placeholder'), PRODUCT_NAME)

    def test_self_order_page_title_does_not_name_a_product(self):
        titles = self.env.ref('pos_self_order.index')._get_combined_arch().xpath('//title')
        self.assertEqual(len(titles), 1)
        self.assertTrue(titles[0].text.strip())
        self.assertNotRegex(titles[0].text, PRODUCT_NAME)

    def test_settings_do_not_offer_stands_ordered_from_odoo(self):
        arch = etree.fromstring(self.env['res.config.settings'].get_view(view_type='form')['arch'])
        self.assertFalse(arch.xpath('//button[@name="get_pos_qr_stands"]'))
        self.assertTrue(arch.xpath('//button[@name="generate_qr_codes_page"]'), 'the other buttons stay')

    def test_pos_templates_drop_the_qr_stand_entries_and_every_xpath_resolves(self):
        for override_rel, core_rel in POS_TEMPLATE_EXTENSIONS:
            with self.subTest(override=override_rel):
                override = etree.parse(os.path.join(MODULE_DIR, override_rel))
                exprs = [node.get('expr') for node in override.getroot().iter('xpath')]
                self.assertTrue(exprs)
                core = etree.parse(os.path.join(get_module_path('pos_self_order'), core_rel))
                for expr in exprs:
                    self.assertTrue(core.getroot().xpath(expr), 'the xpath %s matches the core node' % expr)

    def test_pos_bundle_applies_the_qr_stand_removal_after_the_core_extensions_it_edits(self):
        paths = [path.lstrip('/') for path, _full, _bundle, _mtime in
                 self.env['ir.asset']._get_asset_paths(bundle='point_of_sale._assets_pos', assets_params={})]
        for override_rel, _core_rel in POS_TEMPLATE_EXTENSIONS:
            with self.subTest(override=override_rel):
                own = 'viin_brand_pos_self_order/' + override_rel
                core = 'pos_self_order/' + override_rel
                self.assertIn(own, paths)
                self.assertGreater(paths.index(own), paths.index(core))

    def test_self_order_app_bundle_carries_the_dialog_debrand(self):
        paths = [path.lstrip('/') for path, _full, _bundle, _mtime in
                 self.env['ir.asset']._get_asset_paths(bundle='pos_self_order.assets', assets_params={})]
        for path in (
            'viin_brand/static/src/core/dialog/dialog.js',
            'viin_brand/static/src/core/errors/error_dialogs.js',
            'viin_brand/static/src/core/errors/error_dialogs.xml',
        ):
            with self.subTest(file=path):
                self.assertIn(path, paths)

    def test_bundles_build_with_no_missing_or_malformed_asset(self):
        swallowed = re.compile(r'(?:console\.error|throw new Error)\("(?:[^"\\]|\\.)*"\)')
        for bundle_name in ('point_of_sale._assets_pos', 'pos_self_order.assets'):
            with self.subTest(bundle=bundle_name):
                js = self.env['ir.qweb']._get_asset_bundle(bundle_name, css=False, js=True).js()
                self.assertTrue(js)
                own = [call for call in swallowed.findall((js.raw or b'').decode('utf-8', 'replace'))
                       if 'viin_brand' in call]
                self.assertFalse(own, own)

    def test_the_module_depends_on_viin_brand_whose_hide_list_and_files_it_extends(self):
        self.assertIn('viin_brand', get_manifest('viin_brand_pos_self_order')['depends'])
