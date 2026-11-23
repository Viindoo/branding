# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged
from odoo.tools.translate import TranslationImporter, get_po_paths

from odoo.addons.viin_brand.tests.common import LANG, NoupdateTranslationCase

BRAND_LABEL = 'Company Favicon'


@tagged('post_install', '-at_install')
class TestFaviconSettingTranslation(NoupdateTranslationCase):

    def test_favicon_setting_reads_as_the_website_declares_it(self):
        """The website re-declares the setting; the company wording of viin_brand stays out."""
        xmlid = 'website.field_res_config_settings__favicon'
        field = self.env.ref(xmlid)
        brand_xmlid = 'viin_brand.field_res_config_settings__favicon'
        self.assertIn(brand_xmlid, field._get_external_ids()[field.id])
        self.env['res.lang']._activate_lang(LANG)
        importer = TranslationImporter(self.env.cr, verbose=False)
        for path in get_po_paths('viin_brand', LANG):
            importer.load_file(path, LANG)
        importer.save(overwrite=True)
        brand_vi = self.catalog_translation('viin_brand', BRAND_LABEL, brand_xmlid)
        self.assertEqual(self.translated(field, 'field_description'), brand_vi)

        self.load_catalog('viin_brand')

        for field_name in ('field_description', 'help'):
            with self.subTest(field=field_name):
                english = field.with_context(lang='en_US')[field_name]
                self.assertEqual(
                    self.translated(field, field_name),
                    self.catalog_translation('website', english, xmlid, core=True),
                )
