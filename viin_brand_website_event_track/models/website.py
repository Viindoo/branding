from odoo import models

from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR


class Website(models.Model):
    _inherit = 'website'

    def get_events_app_theme_color(self):
        """Return the colour that the events app asks the browser to paint its frame with.

        The manifest of the app and the pages of the events read it, so the two cannot differ.
        """
        return VIINDOO_BRAND_COLOR
