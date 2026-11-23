import re

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open
from odoo.tools.translate import get_po_paths, translation_file_reader

BRAND_PATTERN = re.compile(r'\bOdoo\b|odoo\.com|Enterprise|bill|pricing|subscription', re.IGNORECASE)
XMLID = 'viin_brand_base_import_module.field_ir_module_module__total_lines_of_code'
MODULES = ['base_import_module', 'viin_brand_base_import_module']


@tagged('post_install', '-at_install')
class TestTotalLinesOfCodeHelp(TransactionCase):
    """The help of the lines of code of a module makes no billing claim and names no other product."""

    def _help(self, lang):
        """Return the help the web client receives for the field, in a language."""
        return self.env['ir.module.module'].with_context(lang=lang).fields_get(
            ['total_lines_of_code'], ['help'])['total_lines_of_code']['help']

    def _catalog_translation(self, lang):
        """Return the translation this module's catalog gives the help in a language."""
        for path in get_po_paths('viin_brand_base_import_module', lang):
            with file_open(path, 'rb', env=self.env) as po_file:
                for row in translation_file_reader(po_file, 'po'):
                    is_help_of_field = row['name'] == 'ir.model.fields,help'
                    if is_help_of_field and '%s.%s' % (row['module'], row.get('imd_name')) == XMLID and row['value']:
                        return row['value']
        raise AssertionError('no help entry %s in the %s catalog' % (XMLID, lang))

    def test_help_in_english_names_no_odoo_and_no_billing(self):
        self.assertNotRegex(self._help('en_US'), BRAND_PATTERN)

    def test_language_with_a_catalog_takes_its_translation(self):
        self.env['res.lang']._activate_lang('vi_VN')
        self.env['ir.module.module']._load_module_terms(MODULES, ['vi_VN'])
        self.assertEqual(self._help('vi_VN'), self._catalog_translation('vi_VN'))

    def test_language_without_a_catalog_shows_the_english(self):
        self.env['res.lang']._activate_lang('fr_FR')
        self.env['ir.module.module']._load_module_terms(MODULES, ['fr_FR'])
        self.assertEqual(self._help('fr_FR'), self._help('en_US'))
