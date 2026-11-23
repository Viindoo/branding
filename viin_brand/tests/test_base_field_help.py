from odoo.tests.common import tagged

from .common import PRODUCT_NAME_IN_ENGLISH, NoupdateTranslationCase

HELPS = {
    'ir.sequence': ('padding', 'viin_brand.field_ir_sequence__padding'),
    'ir.ui.menu': ('group_ids', 'viin_brand.field_ir_ui_menu__group_ids'),
}


@tagged('post_install', '-at_install')
class TestBaseFieldHelp(NoupdateTranslationCase):
    """The helps of the base fields that named the product show the product of the brand."""

    def _help(self, model, name, lang):
        """Return the help the web client receives for a field, in a language."""
        return self.env[model].with_context(lang=lang).fields_get([name], ['help'])[name]['help']

    def _load_language(self, lang):
        self.env['res.lang']._activate_lang(lang)
        self.env['ir.module.module']._load_module_terms(['base', 'viin_brand'], [lang])

    def test_helps_in_english_name_no_odoo(self):
        for model, (name, _xmlid) in HELPS.items():
            with self.subTest(field='%s.%s' % (model, name)):
                self.assertNotRegex(self._help(model, name, 'en_US'), PRODUCT_NAME_IN_ENGLISH)

    def test_languages_with_a_catalog_take_its_translation(self):
        for lang in ('vi_VN', 'de_DE', 'ja_JP'):
            self._load_language(lang)
            for model, (name, xmlid) in HELPS.items():
                with self.subTest(lang=lang, field='%s.%s' % (model, name)):
                    english = self._help(model, name, 'en_US')
                    self.assertEqual(
                        self._help(model, name, lang),
                        self.catalog_translation('viin_brand', english, xmlid, lang=lang),
                    )

    def test_a_language_without_a_catalog_shows_the_branding_english(self):
        self._load_language('fr_FR')
        for model, (name, _xmlid) in HELPS.items():
            with self.subTest(field='%s.%s' % (model, name)):
                self.assertEqual(self._help(model, name, 'fr_FR'), self._help(model, name, 'en_US'))
