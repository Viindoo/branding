from odoo import fields, models
from odoo.tools import BinaryBytes, file_open


class Website(models.Model):
    _inherit = 'website'

    def _default_brand_favicon(self):
        """Return the favicon a newly created website starts with.

        The Viindoo favicon, so a new website is branded out of the box and still shows the
        customer's own value as soon as one is set.
        """
        with file_open('viin_brand/static/img/favicon.ico', 'rb') as f:
            return BinaryBytes(f.read(), filename='favicon.ico')

    # Core binds the default to the function object at class definition, so overriding
    # the method alone would never be picked up.
    favicon = fields.Binary(default=lambda self: self._default_brand_favicon())
