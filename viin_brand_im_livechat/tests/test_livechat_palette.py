# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import ast

from lxml import etree, html

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand_im_livechat import _update_viindoo_livechat_color

BRAND_PURPLE = '#7F4282'
DEFAULT_PURPLE_OF_CORE = '#875A7B'
CUSTOMER_COLOUR = '#123ABC'


@tagged('post_install', '-at_install')
class TestLivechatPalette(TransactionCase):

    def test_a_new_channel_is_created_with_the_brand_colour_on_header_and_button(self):
        channel = self.env['im_livechat.channel'].create({'name': 'Palette channel'})
        self.assertEqual(channel.header_background_color, BRAND_PURPLE)
        self.assertEqual(channel.button_background_color, BRAND_PURPLE)

    def test_installing_the_module_recolours_a_channel_that_still_holds_the_stock_colours(self):
        channel = self.env['im_livechat.channel'].create({
            'name': 'Stock channel',
            'header_background_color': DEFAULT_PURPLE_OF_CORE,
            'button_background_color': DEFAULT_PURPLE_OF_CORE,
        })
        _update_viindoo_livechat_color(self.env)
        self.assertEqual(channel.header_background_color, BRAND_PURPLE)
        self.assertEqual(channel.button_background_color, BRAND_PURPLE)

    def test_installing_the_module_keeps_a_colour_the_customer_chose(self):
        customised = self.env['im_livechat.channel'].create({
            'name': 'Customised channel',
            'header_background_color': CUSTOMER_COLOUR,
            'button_background_color': CUSTOMER_COLOUR,
        })
        half_customised = self.env['im_livechat.channel'].create({
            'name': 'Half customised channel',
            'header_background_color': CUSTOMER_COLOUR,
            'button_background_color': DEFAULT_PURPLE_OF_CORE,
        })
        _update_viindoo_livechat_color(self.env)
        self.assertEqual(customised.header_background_color, CUSTOMER_COLOUR)
        self.assertEqual(customised.button_background_color, CUSTOMER_COLOUR)
        self.assertEqual(half_customised.header_background_color, CUSTOMER_COLOUR)
        self.assertEqual(half_customised.button_background_color, BRAND_PURPLE)

    def test_the_reset_buttons_of_the_form_restore_the_colours_a_new_channel_gets(self):
        arch = self.env['im_livechat.channel'].get_views([[False, 'form']])['views']['form']['arch']
        channel = self.env['im_livechat.channel'].create({'name': 'Reset channel'})
        resets = {}
        for widget in etree.fromstring(arch).xpath("//widget[@name='colors_reset_button']"):
            resets.update(ast.literal_eval(widget.get('options'))['default_colors'])
        self.assertEqual(resets['header_background_color'], channel.header_background_color)
        self.assertEqual(resets['button_background_color'], channel.button_background_color)

    def test_the_support_page_gradient_runs_in_the_brand_purples(self):
        arch = self.env.ref('im_livechat.support_page')._get_combined_arch()
        style = ' '.join(arch.xpath('//head/style//text()')).upper()
        self.assertIn('#592E5B', style)
        self.assertIn(BRAND_PURPLE, style)

    def test_the_canned_response_tip_loads_its_image_from_this_database(self):
        tip = self.env.ref('im_livechat.digest_tip_im_livechat_0')
        sources = html.fromstring(tip.tip_description).xpath('//img/@src')
        self.assertTrue(sources)
        for source in sources:
            self.assertNotIn('odoocdn.com', source)
            self.assertTrue(source.startswith('/'), source)
