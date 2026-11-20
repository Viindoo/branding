from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged

CORE_STOCK_MOVE = 'odoo.addons.purchase_mrp.models.stock_move.StockMove._get_valuation_price_and_qty'


@tagged('post_install', '-at_install')
class TestKitValuationErrorBrand(TransactionCase):

    def test_zero_kit_valuation_error_names_viindoo_not_odoo(self):
        core_error = UserError(
            'Odoo is not able to generate the anglo saxon entries. The total valuation of Kit is zero.')
        move = self.env['stock.move']
        with patch(CORE_STOCK_MOVE, side_effect=core_error), self.assertRaises(UserError) as caught:
            move._get_valuation_price_and_qty(self.env['account.move.line'], self.env.company.currency_id)
        message = caught.exception.args[0]
        self.assertNotRegex(message, r'\bOdoo\b')
        self.assertIn('Viindoo is not able to generate the anglo saxon entries', message)

    def test_a_valuation_without_error_is_returned_untouched(self):
        move = self.env['stock.move']
        with patch(CORE_STOCK_MOVE, return_value=(10.0, 2.0)):
            result = move._get_valuation_price_and_qty(self.env['account.move.line'], self.env.company.currency_id)
        self.assertEqual(result, (10.0, 2.0))
