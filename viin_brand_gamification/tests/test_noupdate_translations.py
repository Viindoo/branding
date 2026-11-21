# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import LANG, NoupdateTranslationCase
from odoo.addons.viin_brand_gamification import post_init_hook


@tagged('post_install', '-at_install')
class TestBadgeMailTranslation(NoupdateTranslationCase):

    def test_badge_mail_of_a_language_loaded_before_the_module_names_viindoo(self):
        self.load_stock_then_branding_catalog(['gamification'], 'viin_brand_gamification')
        template = self.env.ref('gamification.email_template_badge_received')
        self.assertHoldsStockWording(self.translated(template, 'body_html'))
        self.load_catalog('viin_brand_gamification')
        self.assertNamesNoOdoo(self.translated(template, 'body_html'))

    def test_badge_mail_of_a_language_loaded_with_the_module_names_viindoo(self):
        """The install loads the catalog of the module, then its hook writes the English the catalog translates."""
        template = self.env.ref('gamification.email_template_badge_received')
        branded = str(template.with_context(lang='en_US').body_html)
        stock_english = branded.replace('https://viindoo.com', 'https://www.odoo.com').replace(
            '>Viindoo</a>', '>Odoo</a>',
        )
        self.assertNotEqual(stock_english, branded)
        template.with_context(lang='en_US').body_html = stock_english
        self.env['res.lang']._activate_lang(LANG)
        self.env['ir.module.module']._load_module_terms(['gamification', 'viin_brand_gamification'], [LANG])
        self.assertHoldsStockWording(self.translated(template, 'body_html'))

        post_init_hook(self.env)

        self.assertNamesNoOdoo(self.translated(template, 'body_html'))
