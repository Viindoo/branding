from odoo import _, http

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleBrand(WebsiteSale):

    @http.route()
    def add_product_media(self, media, product_product_id, product_template_id, combination_ids=None, **kwargs):
        """Give a product video that comes without a name a neutral name, not the one of Odoo.

        ``type`` (image or video) comes in ``kwargs``: a parameter of that name would hide the builtin.
        """
        if kwargs.get('type') == 'video':
            media = [{'name': _("Video"), **item} for item in media]
        return super().add_product_media(
            media, product_product_id=product_product_id, product_template_id=product_template_id,
            combination_ids=combination_ids, **kwargs,
        )
