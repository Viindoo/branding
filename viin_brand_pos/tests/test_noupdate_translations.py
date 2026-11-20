# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo.tests.common import tagged
from odoo.tools import file_open

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestSneakersTranslation(NoupdateTranslationCase):

    def test_sneakers_name_of_a_language_loaded_before_the_module_is_neutral(self):
        with file_open('point_of_sale/static/img/product_odoo_sneakers.png', 'rb') as image:
            product = self.env['product.product'].create({
                'name': 'Odoo Sneakers', 'image_1920': base64.b64encode(image.read()),
            })
        for model, record, name in (
            ('product.product', product, 'product_odoo_sneakers'),
            ('product.template', product.product_tmpl_id, 'product_odoo_sneakers_product_template'),
        ):
            self.env['ir.model.data'].create({
                'module': 'point_of_sale', 'name': name, 'model': model, 'res_id': record.id, 'noupdate': True,
            })
        self.load_stock_then_branding_catalog(['point_of_sale'], 'viin_brand_pos')
        self.assertHoldsStockWording(self.translated(product.product_tmpl_id, 'name'))
        self.env['pos.config']._debrand_clothes_scenario()
        self.assertNamesNoOdoo(self.translated(product.product_tmpl_id, 'name'), product_name=None)
