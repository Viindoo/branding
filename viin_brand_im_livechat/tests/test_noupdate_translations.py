# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestWelcomeBotTranslation(NoupdateTranslationCase):

    def test_welcome_bot_title_of_a_language_loaded_before_the_module_names_viindoo(self):
        bot = self.env['chatbot.script'].create({'title': 'Odoo'})
        self.env['ir.model.data'].create({
            'module': 'im_livechat', 'name': 'chatbot_script_welcome_bot_demo', 'model': 'chatbot.script',
            'res_id': bot.id, 'noupdate': True,
        })
        self.load_stock_then_branding_catalog(['im_livechat'], 'viin_brand_im_livechat')
        bot.title = 'Viindoo'
        self.assertHoldsStockWording(self.translated(bot, 'title'))
        self.load_catalog('viin_brand_im_livechat')
        self.assertNamesNoOdoo(self.translated(bot, 'title'))
