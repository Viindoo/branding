# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from lxml import etree

from odoo.tests.common import tagged

from .common import NoupdateTranslationCase

HINT = "//sheet/div[contains(concat(' ', @class, ' '), ' alert-info ')]"


@tagged('post_install', '-at_install')
class TestViewEditorHint(NoupdateTranslationCase):

    def _hint(self, lang):
        """Return the text of the hint of the view form as a user of the language reads it."""
        view = self.env.ref('base.view_view_form')
        arch = self.env['ir.ui.view'].with_context(lang=lang).get_view(view.id, 'form')['arch']
        hints = etree.fromstring(arch).xpath(HINT)
        self.assertEqual(len(hints), 1)
        return ' '.join(' '.join(hints[0].itertext()).split())

    def test_view_editor_hint_recommends_no_product_viindoo_lacks(self):
        """The view form advises inherited views, not a customization product."""
        text = self._hint('en_US')
        self.assertIn('inherited views', text)
        self.assertNotIn('Studio', text)
        self.assertNotIn('Odoo', text)

    def test_view_editor_hint_composes_in_other_languages(self):
        """The hint is located by its place, so a translated form composes with it in every language."""
        hint_view = self.env.ref('viin_brand.view_view_form')
        [english] = hint_view._fields['arch_db'].get_trans_terms(hint_view.with_context(lang='en_US').arch_db)
        for lang, modules in (('vi_VN', ['base', 'viin_brand']), ('ar_001', ['base'])):
            with self.subTest(lang=lang):
                self.env['res.lang']._activate_lang(lang)
                self.env['ir.module.module']._load_module_terms(modules, [lang])
                expected = english
                if 'viin_brand' in modules:
                    expected = self.catalog_translation('viin_brand', english, 'viin_brand.view_view_form')
                self.assertEqual(self._hint(lang), ' '.join(re.sub(r'<br\s*/?>', ' ', expected).split()))
