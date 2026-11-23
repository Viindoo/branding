from odoo.tests.common import tagged
from odoo.tools.convert import convert_file
from odoo.tools.translate import ParsedTranslation

from .common import PRODUCT_NAME_IN_ENGLISH, NoupdateTranslationCase

FRENCH = 'fr_FR'
CONTACTS = 'base.action_partner_form'
FROM_FILTER = 'viin_brand.field_ir_mail_server__from_filter'
STOCK_CONTACTS_HELP = (
    '<p class="o_view_nocontent_smiling_face">Create a Contact in your address book</p>'
    '<p>Odoo helps you track all activities related to your contacts.</p>'
)


@tagged('post_install', '-at_install')
class TestBrandingEnglishFallback(NoupdateTranslationCase):
    """A language that no branding catalog covers shows the English the branding gives a record.

    French has no catalog in viin_brand: the stock French catalog translates the English the records
    have without the branding, and names Odoo.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.from_filter = cls.env.ref(FROM_FILTER)
        cls.contacts = cls.env.ref(CONTACTS)

    def _load_language(self, lang, modules=('base', 'viin_brand')):
        """Activate a language and load the catalogs of ``modules`` in it, as activating it does."""
        self.env['res.lang']._activate_lang(lang)
        self.env['ir.module.module']._load_module_terms(list(modules), [lang])

    def _install_viin_brand_after_the_language(self):
        """Give the records their stock English and French, then load viin_brand as its install does."""
        self.contacts.with_context(lang='en_US').help = STOCK_CONTACTS_HELP
        self._load_language(FRENCH, modules=('base',))
        convert_file(self.env, 'viin_brand', 'data/ir_actions_data.xml', None, 'init')
        self.assertRegex(self._help(self.contacts, FRENCH), PRODUCT_NAME_IN_ENGLISH, 'the stock French survives')
        self.env['ir.module.module']._load_module_terms(['viin_brand'], [FRENCH])

    def _help(self, record, lang):
        return str(record.with_context(lang=lang).help or '')

    def _branding_terms(self, record):
        """Return the English terms of the help of a record that the stock help does not have."""
        field = record._fields['help']
        stock = set(ParsedTranslation(field, STOCK_CONTACTS_HELP).terms)
        return [term for term in ParsedTranslation(field, self._help(record, 'en_US')).terms if term not in stock]

    def test_language_added_after_the_branding_shows_the_branding_english(self):
        self._load_language(FRENCH)
        self.assertEqual(self._help(self.from_filter, FRENCH), self._help(self.from_filter, 'en_US'))
        french = self._help(self.contacts, FRENCH)
        self.assertNotRegex(french, PRODUCT_NAME_IN_ENGLISH)
        for term in self._branding_terms(self.contacts):
            self.assertIn(term, french)

    def test_core_catalog_loaded_alone_shows_the_branding_english(self):
        self._load_language(FRENCH, modules=('base',))
        self.assertEqual(self._help(self.from_filter, FRENCH), self._help(self.from_filter, 'en_US'))

    def test_branding_installed_after_the_language_shows_the_branding_english(self):
        self._install_viin_brand_after_the_language()
        french = self._help(self.contacts, FRENCH)
        self.assertNotRegex(french, PRODUCT_NAME_IN_ENGLISH)
        for term in self._branding_terms(self.contacts):
            self.assertIn(term, french)
        stock_term = ParsedTranslation(self.contacts._fields['help'], STOCK_CONTACTS_HELP).terms[0]
        self.assertIn(self.catalog_translation('base', stock_term, CONTACTS, lang=FRENCH, core=True), french)
        self.assertEqual(self._help(self.from_filter, FRENCH), self._help(self.from_filter, 'en_US'))

    def test_language_with_a_branding_catalog_keeps_its_translation(self):
        english = self._help(self.from_filter, 'en_US')
        self._load_language('vi_VN')
        self.assertEqual(
            self._help(self.from_filter, 'vi_VN'),
            self.catalog_translation('viin_brand', english, FROM_FILTER, lang='vi_VN'),
        )
        self._load_language('de_DE')
        german = self._help(self.contacts, 'de_DE')
        for term in self._branding_terms(self.contacts):
            self.assertIn(self.catalog_translation('viin_brand', term, CONTACTS, lang='de_DE'), german)

    def test_translation_a_user_wrote_is_kept(self):
        self._load_language(FRENCH, modules=('base',))
        self.from_filter.update_field_translations('help', {FRENCH: 'Mon aide sur odoo.com'})
        self.env['ir.module.module']._load_module_terms(['base', 'viin_brand'], [FRENCH])
        self.assertEqual(self._help(self.from_filter, FRENCH), 'Mon aide sur odoo.com')

    def test_term_a_user_translated_is_kept(self):
        self._install_viin_brand_after_the_language()
        [term] = self._branding_terms(self.contacts)
        self.contacts.update_field_translations('help', {FRENCH: {term: 'Mon suivi de contacts'}})
        self.env['ir.module.module']._load_module_terms(['base', 'viin_brand'], [FRENCH])
        self.assertIn('Mon suivi de contacts', self._help(self.contacts, FRENCH))

    def test_loading_again_changes_nothing(self):
        self._install_viin_brand_after_the_language()
        first = (self._help(self.from_filter, FRENCH), self._help(self.contacts, FRENCH))
        self.env['ir.module.module']._load_module_terms(['base', 'viin_brand'], [FRENCH])
        self.assertEqual((self._help(self.from_filter, FRENCH), self._help(self.contacts, FRENCH)), first)
