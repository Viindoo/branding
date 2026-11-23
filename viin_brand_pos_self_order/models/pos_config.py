from odoo import Command, api, models

CORE_LANDING_IMAGE_PREFIX = '/pos_self_order/static/img/landing_'
LANDING_IMAGE_PREFIX = '/viin_brand_pos_self_order/static/img/landing_'


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _prepare_self_order_splash_screen(self, vals_list, is_new=False):
        result = super()._prepare_self_order_splash_screen(vals_list, is_new=is_new)
        for vals in vals_list:
            for command in vals.get('self_ordering_image_home_ids') or []:
                if command[0] != Command.CREATE:
                    continue
                url = command[2].get('url') or ''
                if url.startswith(CORE_LANDING_IMAGE_PREFIX):
                    command[2]['url'] = self._get_brand_landing_image_url(url)
        return result

    @api.model
    def _use_brand_landing_images(self):
        """Point the core landing images attached to kiosks to the images of this module.

        Runs whenever the module is installed or updated; an image the user uploaded is left as it is.
        """
        attachments = self.env['ir.attachment'].search([
            ('type', '=', 'url'),
            ('res_model', '=', 'pos.config'),
            ('url', '=like', CORE_LANDING_IMAGE_PREFIX + '%'),
        ])
        for attachment in attachments:
            attachment.url = self._get_brand_landing_image_url(attachment.url)

    @api.model
    def _get_brand_landing_image_url(self, core_url):
        return LANDING_IMAGE_PREFIX + core_url[len(CORE_LANDING_IMAGE_PREFIX):]
