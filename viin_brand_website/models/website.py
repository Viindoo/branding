import base64
import logging

from odoo import fields, models, tools

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    def _default_brand_favicon(self):
        """Return the favicon a newly created website starts with.

        The Viindoo favicon, so a new website is branded out of the box and still shows the
        customer's own value as soon as one is set; core's default when the asset is missing.
        """
        try:
            with tools.file_open('viin_brand/static/img/favicon.ico', 'rb') as f:
                return base64.b64encode(f.read())
        except (FileNotFoundError, OSError):
            _logger.warning("Brand favicon not found on the addons path; using core's default favicon")
            return super()._default_favicon()

    # Core binds the default to the function object at class definition, so overriding
    # the method alone would never be picked up.
    favicon = fields.Binary(default=lambda self: self._default_brand_favicon())
