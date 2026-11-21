import re

from lxml import etree

from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open

CORE_TEMPLATE = 'static/src/import_data_content/import_data_content.xml'


@tagged('post_install', '-at_install')
class TestImportTemplates(TransactionCase):

    def test_import_screen_wording_is_served_in_the_backend_bundle(self):
        js = self.env['ir.qweb']._get_asset_bundle('web.assets_backend', css=False, js=True).js()
        served = re.sub(r'\s+', ' ', (js.raw or b'').decode('utf-8', 'replace'))
        self.assertIn('Viindoo can try auto-detecting', served)
        self.assertIn('Viindoo Field', served)

    def test_every_xpath_of_the_extension_resolves_against_the_core_template(self):
        with file_open('viin_brand_base_import/' + CORE_TEMPLATE) as file:
            exprs = [node.get('expr') for node in etree.parse(file).getroot().iter('xpath')]
        self.assertTrue(exprs)
        core = etree.parse(get_module_path('base_import') + '/' + CORE_TEMPLATE)
        for expr in exprs:
            with self.subTest(xpath=expr):
                self.assertTrue(core.getroot().xpath(expr))
