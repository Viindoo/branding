# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestDigestTranslation(NoupdateTranslationCase):

    def test_default_digest_name_of_a_language_loaded_before_the_module_names_viindoo(self):
        self.load_stock_then_branding_catalog(['digest'], 'viin_brand_digest')
        digest = self.env.ref('digest.digest_digest_default')
        self.assertHoldsStockWording(self.translated(digest, 'name'))
        self.load_catalog('viin_brand_digest')
        self.assertNamesNoOdoo(self.translated(digest, 'name'))

    def _hold_core_translation(self, tip):
        """Give the tip the translation of the stock catalog, then the English of the module.

        The stock English is written and translated first, as an update of the stock module leaves
        the tip, and the English of the module comes after, so that the stock wording stays in the
        language of the user.
        """
        english = {field: str(tip.with_context(lang='en_US')[field]) for field in ('name', 'tip_description')}
        stock_english = {field: value.replace('Viindoo', 'Odoo') for field, value in english.items()}
        tip.with_context(lang='en_US').write(stock_english)
        self.env['res.lang']._activate_lang('vi_VN')
        self.env['ir.module.module']._load_module_terms(['digest'], ['vi_VN'])
        tip.with_context(lang='en_US').write(english)

    def test_tips_of_a_language_loaded_before_the_module_name_viindoo(self):
        tip_2 = self.env.ref('digest.digest_tip_digest_2')
        tip_3 = self.env.ref('digest.digest_tip_digest_3')
        self._hold_core_translation(tip_2)
        self._hold_core_translation(tip_3)
        self.assertIn('Odoo', self.translated(tip_2, 'name'))
        self.load_catalog('viin_brand_digest')
        for tip, field in ((tip_2, 'name'), (tip_2, 'tip_description'), (tip_3, 'tip_description')):
            value = self.translated(tip, field)
            self.assertNotRegex(value, r'Odoo')
            self.assertIn('Viindoo', value)

    def test_tip_name_a_user_wrote_survives_the_reload(self):
        tip = self.env.ref('digest.digest_tip_digest_2')
        self._hold_core_translation(tip)
        tip.with_context(lang='vi_VN').name = 'Mẹo của công ty'
        self.load_catalog('viin_brand_digest')
        self.assertEqual(self.translated(tip, 'name'), 'Mẹo của công ty')
