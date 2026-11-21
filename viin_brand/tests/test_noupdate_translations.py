from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.translate import TranslationImporter

from .common import LANG, NoupdateTranslationCase

MODEL_TAG = 'res.partner.category,name'
MODEL_HELP = 'ir.actions.act_window,help'
TAG_XMLID = 'viin_brand.noupdate_translation_tag'
HELP_XMLID = 'viin_brand.noupdate_translation_help'
BRANDING_MODULE = 'viin_brand_noupdate_translation_fixture'
OTHER_MODULE = 'noupdate_translation_fixture'
ALIAS_BRANDING_MODULE = 'viin_brand_alias_fixture'
PO_DIRECTORY = 'viin_brand/tests/po/'
STOCK_ENGLISH = {
    'name': 'Odoo tag',
    'help': '<p>One dedicated to advanced Odoo developers, one for new developers.</p><p>Start now.</p>',
}
BRAND_ENGLISH = {
    'name': 'Viindoo tag',
    'help': '<p>One dedicated to advanced Viindoo developers, one for new developers.</p><p>Start now.</p>',
}
STOCK_VI = {
    'name': 'Nhãn Odoo lõi',
    'help': '<p>Một phòng cho lập trình viên Odoo nâng cao.</p><p>Bắt đầu ngay.</p>',
}
BRAND_VI = {
    'name': 'Nhãn Viindoo',
    'help': '<p>Một phòng cho lập trình viên Viindoo nâng cao.</p><p>Bắt đầu ngay.</p>',
}


@tagged('post_install', '-at_install')
class TestReapplyNoupdateTranslations(TransactionCase):
    """Records as a database holds them when its language was loaded before the branding module.

    The stock catalog translated the stock English of each record, then the branding module wrote
    its own English, which the noupdate record keeps the stock translation of.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.lang']._activate_lang(LANG)
        cls.tag = cls._create_noupdate_record('res.partner.category', {'name': STOCK_ENGLISH['name']}, TAG_XMLID)
        cls.act_help = cls._create_noupdate_record(
            'ir.actions.act_window',
            {'name': 'Fixture action', 'res_model': 'res.partner', 'help': STOCK_ENGLISH['help']},
            HELP_XMLID,
        )
        cls.paths = {'viin_brand': PO_DIRECTORY + 'stock.po', BRANDING_MODULE: PO_DIRECTORY + 'branding.po'}

    @classmethod
    def _create_noupdate_record(cls, model, values, xmlid):
        record = cls.env[model].create(values)
        module, name = xmlid.split('.')
        cls.env['ir.model.data'].create({
            'module': module, 'name': name, 'model': model, 'res_id': record.id, 'noupdate': True,
        })
        return record

    def _load_stock_catalog(self):
        importer = TranslationImporter(self.env.cr, verbose=False)
        importer.load_file(self.paths['viin_brand'], LANG)
        importer.save()

    def _write_branding_english(self):
        self.tag.name = BRAND_ENGLISH['name']
        self.act_help.help = BRAND_ENGLISH['help']

    def _hold_stock_translation(self):
        """Translate the stock English, then give the record the branding English, as the install does."""
        self._load_stock_catalog()
        self._write_branding_english()
        self.assertIn('Odoo', self._value(self.act_help, 'help'), 'the stock translation survives the English')

    def _reapply(self):
        def po_paths(module_name, lang):
            return [self.paths[module_name]] if module_name in self.paths else []

        with patch('odoo.addons.viin_brand.models.ir_module_module.get_po_paths', po_paths):
            self.env['ir.module.module']._reapply_noupdate_translations(BRANDING_MODULE)

    def _value(self, record, field_name):
        return str(record.with_context(lang=LANG)[field_name])

    def test_value_the_stock_catalog_gave_takes_the_branding_catalog(self):
        self._hold_stock_translation()
        self.assertEqual(self._value(self.tag, 'name'), STOCK_VI['name'])
        self._reapply()
        self.assertEqual(self._value(self.tag, 'name'), BRAND_VI['name'])
        self.assertEqual(self._value(self.act_help, 'help'), BRAND_VI['help'])

    def test_value_without_translation_takes_the_branding_catalog(self):
        self._write_branding_english()
        self._reapply()
        self.assertEqual(self._value(self.tag, 'name'), BRAND_VI['name'])
        self.assertEqual(self._value(self.act_help, 'help'), BRAND_VI['help'])

    def test_original_english_text_the_stock_catalog_leaves_untranslated_is_replaced(self):
        self.paths = dict(self.paths, viin_brand=PO_DIRECTORY + 'stock_untranslated.po')
        self._hold_stock_translation()
        self._reapply()
        self.assertEqual(self._value(self.act_help, 'help'), BRAND_VI['help'])

    def test_value_a_user_wrote_is_kept(self):
        self._hold_stock_translation()
        edited = '<p>Một phòng cho lập trình viên Odoo nâng cao.</p><p>Ý của tôi.</p>'
        self.tag.with_context(lang=LANG).name = 'Nhãn của tôi'
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE ir_act_window SET help = help || jsonb_build_object(%s, %s::text) WHERE id = %s",
            [LANG, edited, self.act_help.id],
        )
        self.act_help.invalidate_recordset()
        self.assertEqual(self._value(self.act_help, 'help'), edited)
        self._reapply()
        self.assertEqual(self._value(self.tag, 'name'), 'Nhãn của tôi')
        self.assertEqual(self._value(self.act_help, 'help'), edited)

    def test_english_text_is_not_changed(self):
        self._hold_stock_translation()
        self._reapply()
        self.assertEqual(self.tag.with_context(lang='en_US').name, BRAND_ENGLISH['name'])
        self.assertEqual(self.act_help.with_context(lang='en_US').help, BRAND_ENGLISH['help'])

    def test_applying_twice_gives_the_same_values(self):
        self._hold_stock_translation()
        self._reapply()
        first = (self._value(self.tag, 'name'), self._value(self.act_help, 'help'))
        self._reapply()
        self.assertEqual((self._value(self.tag, 'name'), self._value(self.act_help, 'help')), first)

    def _make_not_noupdate(self):
        self.env['ir.model.data'].search([
            ('module', '=', 'viin_brand'), ('name', '=', 'noupdate_translation_tag'),
        ]).noupdate = False

    def test_record_that_is_not_noupdate_takes_the_branding_catalog_too(self):
        self._hold_stock_translation()
        self._make_not_noupdate()
        self._reapply()
        self.assertEqual(self._value(self.tag, 'name'), BRAND_VI['name'])

    def test_value_a_user_wrote_in_a_record_that_is_not_noupdate_is_kept(self):
        self._hold_stock_translation()
        self._make_not_noupdate()
        self.tag.with_context(lang=LANG).name = 'Nhãn của tôi'
        self._reapply()
        self.assertEqual(self._value(self.tag, 'name'), 'Nhãn của tôi')

    def _name_tag_by_other_modules(self):
        """Give the tag the external ids of a core-like and a branding module, as a field several modules declare."""
        for module in (OTHER_MODULE, ALIAS_BRANDING_MODULE):
            self.env['ir.model.data'].create({
                'module': module, 'name': 'alias_tag', 'model': 'res.partner.category', 'res_id': self.tag.id,
            })
        self.paths = dict(self.paths, **{
            OTHER_MODULE: PO_DIRECTORY + 'alias_stock.po',
            ALIAS_BRANDING_MODULE: PO_DIRECTORY + 'alias_branding.po',
        })

    def test_record_several_catalogs_translate_takes_the_branding_one_when_this_entry_is_stale(self):
        """This catalog's entry names an older English; of the two catalogs translating the current one, branding wins."""
        self._hold_stock_translation()
        self._name_tag_by_other_modules()
        self.paths[BRANDING_MODULE] = PO_DIRECTORY + 'branding_stale.po'
        self._reapply()
        self.assertEqual(self._value(self.tag, 'name'), 'Nhãn Viindoo khác')

    def test_value_a_user_wrote_in_a_record_several_catalogs_name_is_kept(self):
        self._hold_stock_translation()
        self._name_tag_by_other_modules()
        self.tag.with_context(lang=LANG).name = 'Nhãn của tôi'
        self._reapply()
        self.assertEqual(self._value(self.tag, 'name'), 'Nhãn của tôi')

    def _load_catalog(self, module_name):
        """Load a module's catalog as an install, an update or a new language does."""
        paths = dict(self.paths, **{OTHER_MODULE: self.paths[BRANDING_MODULE]})

        def po_paths(name, lang):
            return [paths[name]] if name in paths else []

        target = 'odoo.addons.viin_brand.models.ir_module_module.get_po_paths'
        with patch(target, po_paths):
            self.env['ir.module.module']._load_module_terms([module_name], [LANG])

    def test_catalog_load_of_a_branding_module_applies_its_catalog(self):
        self._hold_stock_translation()
        self._load_catalog(BRANDING_MODULE)
        self.assertEqual(self._value(self.tag, 'name'), BRAND_VI['name'])
        self.assertEqual(self._value(self.act_help, 'help'), BRAND_VI['help'])

    def test_catalog_load_of_another_module_keeps_the_stock_translation(self):
        self._hold_stock_translation()
        self._load_catalog(OTHER_MODULE)
        self.assertEqual(self._value(self.tag, 'name'), STOCK_VI['name'])
        self.assertIn('Odoo', self._value(self.act_help, 'help'))


@tagged('post_install', '-at_install')
class TestBrandingCatalogLoad(NoupdateTranslationCase):

    def test_contacts_empty_state_of_a_language_loaded_first_names_viindoo(self):
        """The language comes first; the branding English keeps the stock wording."""
        xmlid = 'base.action_partner_form'
        brand_term = 'Viindoo helps you track all activities related to your contacts.'
        stock_term = 'Odoo helps you track all activities related to your contacts.'
        action = self.env.ref(xmlid)
        english = action.with_context(lang='en_US').help
        self.assertIn(brand_term, english)
        action.with_context(lang='en_US').help = english.replace(brand_term, stock_term)
        self.env['res.lang']._activate_lang(LANG)
        self.env['ir.module.module']._load_module_terms(['base'], [LANG])
        action.with_context(lang='en_US').help = english
        stock_vi = self.catalog_translation('base', stock_term, xmlid)
        self.assertIn(stock_vi, self.translated(action, 'help'))

        self.load_catalog('viin_brand')

        help_vi = self.translated(action, 'help')
        brand_vi = self.catalog_translation('viin_brand', brand_term, xmlid)
        self.assertIn(brand_vi, help_vi)
        self.assertNotIn(stock_vi, help_vi)

    def test_field_help_a_core_module_declares_too_takes_the_branding_catalog(self):
        """The field row of a language added later holds the core catalog's translation first."""
        xmlid = 'viin_brand.field_ir_mail_server__from_filter'
        field = self.env.ref(xmlid)
        self.assertIn('base.field_ir_mail_server__from_filter', field._get_external_ids()[field.id])
        self.env['res.lang']._activate_lang(LANG)
        self.env['ir.module.module']._load_module_terms(['base'], [LANG], overwrite=True)
        self.assertHoldsStockWording(self.translated(field, 'help'))

        self.load_catalog('viin_brand')

        help_vi = self.translated(field, 'help')
        english = field.with_context(lang='en_US').help
        self.assertEqual(help_vi, self.catalog_translation('viin_brand', english, xmlid))
