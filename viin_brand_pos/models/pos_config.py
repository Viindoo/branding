import base64

from odoo import api, models
from odoo.tools import file_open

DEMO_PRODUCT_XMLID = 'point_of_sale.product_odoo_sneakers'
# Plain lookup key: the name the clothes scenario gives to its sneakers.
CORE_DEMO_PRODUCT_NAME = 'Odoo Sneakers'
DEMO_PRODUCT_NAME = 'Sneakers'
DEMO_PRODUCT_IMAGE = 'viin_brand_pos/static/img/product_sneakers.png'


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _load_onboarding_clothes_demo_data(self, with_demo_data=True):
        result = super()._load_onboarding_clothes_demo_data(with_demo_data)
        self._debrand_clothes_scenario()
        return result

    @api.model
    def _debrand_clothes_scenario(self):
        """Give the sneakers of the clothes scenario a neutral name, image and translations.

        Runs whenever the scenario is loaded.

        A product the user has renamed is left as it is.
        """
        product = self.env.ref(DEMO_PRODUCT_XMLID, raise_if_not_found=False)
        if product and product.name == CORE_DEMO_PRODUCT_NAME:
            with file_open(DEMO_PRODUCT_IMAGE, 'rb') as image:
                product.write({'name': DEMO_PRODUCT_NAME, 'image_1920': base64.b64encode(image.read())})
        if product and product.name == DEMO_PRODUCT_NAME:
            self.env['ir.module.module']._reapply_noupdate_translations('viin_brand_pos')
