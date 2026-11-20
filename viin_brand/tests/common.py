import re
from types import SimpleNamespace
from unittest.mock import patch

from odoo.tests.common import TransactionCase
from odoo.tools import file_open
from odoo.tools.translate import (
    TranslationImporter,
    get_po_paths,
    translation_file_reader,
)

LANG = 'vi_VN'
PRODUCT_NAME_IN_ENGLISH = re.compile(r'\bOdoo\b|(?i:odoo\.com)')


class NoupdateTranslationCase(TransactionCase):
    """A database whose language was loaded before the branding module reached it.

    The record keeps the translation of the stock catalog; loading the catalog of the
    branding module, as its install or update does, is what applies its wording.
    """

    def load_stock_then_branding_catalog(self, stock_modules, branding_module):
        """Translate with the stock catalogs, then the branding one with core alone.

        The core loader keeps the translations the records already hold.
        """
        self.env['res.lang']._activate_lang(LANG)
        self.env['ir.module.module']._load_module_terms(stock_modules, [LANG])
        importer = TranslationImporter(self.env.cr, verbose=False)
        for path in get_po_paths(branding_module, LANG):
            importer.load_file(path, LANG)
        importer.save()

    def load_catalog(self, module):
        """Load the catalog of a module as its install or update does after its data."""
        self.env['ir.module.module']._load_module_terms([module], [LANG])

    def catalog_translation(self, module, source, xmlid):
        """Return the translation a module's catalog gives a source text of a record.

        :param xmlid: the external id of the record the catalog entry names
        """
        for path in get_po_paths(module, LANG):
            with file_open(path, 'rb', env=self.env) as po_file:
                for row in translation_file_reader(po_file, 'po'):
                    row_xmlid = '%s.%s' % (row['module'], row.get('imd_name'))
                    if row_xmlid == xmlid and row['src'] == source and row['value']:
                        return row['value']
        raise AssertionError('no %s entry of %s for %r' % (module, xmlid, source))

    def translated(self, record, field_name):
        """Return the value of a field of the record in the test language."""
        return str(record.with_context(lang=LANG)[field_name] or '')

    def assertHoldsStockWording(self, value):
        """Assert that the value still names Odoo, as the stock catalog worded it."""
        self.assertRegex(value, PRODUCT_NAME_IN_ENGLISH, 'stock wording expected')

    def assertNamesNoOdoo(self, value, product_name='Viindoo'):
        """Assert that the value does not name Odoo, and names the product when ``product_name`` is given."""
        self.assertNotRegex(value, PRODUCT_NAME_IN_ENGLISH)
        if product_name:
            self.assertIn(product_name, value)


class HiddenMenuCase(TransactionCase):
    """A database where branding modules keep the menus of paid services hidden."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = cls.env.ref('base.user_admin')
        cls.admin.group_ids |= cls.env.ref('base.group_no_one')

    def web_client_menu_ids(self):
        """Return the ids of the menus the web client shows the administrator in debug.

        The debug mode shows the technical menus, where several hidden menus live; the
        menu model reads it from the session of the request.
        """
        debug_request = SimpleNamespace(session=SimpleNamespace(debug='1'))
        with patch('odoo.addons.base.models.ir_ui_menu.request', debug_request):
            menus = self.env['ir.ui.menu'].with_user(self.admin).load_menus('1')
        return set(menus) - {'root'}
