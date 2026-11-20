from odoo import models
from odoo.exceptions import UserError

from odoo.addons.viin_brand.tools import debrand_exception


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_valuation_price_and_qty(self, related_aml, to_curr):
        try:
            return super()._get_valuation_price_and_qty(related_aml, to_curr)
        except UserError as error:
            raise debrand_exception(error) from error
