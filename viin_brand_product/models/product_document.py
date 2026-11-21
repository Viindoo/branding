from odoo import api, models
from odoo.exceptions import ValidationError

# The example URL of the core message, and the one that replaces it.
CORE_EXAMPLE_URL = 'https://www.odoo.com'
NEUTRAL_EXAMPLE_URL = 'https://example.com'


class ProductDocument(models.Model):
    _inherit = 'product.document'

    @api.onchange('url')
    def _onchange_url(self):
        try:
            return super()._onchange_url()
        except ValidationError as error:
            message, *rest = error.args
            error.args = (message.replace(CORE_EXAMPLE_URL, NEUTRAL_EXAMPLE_URL), *rest)
            raise
