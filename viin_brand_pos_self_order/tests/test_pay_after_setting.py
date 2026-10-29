from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPayAfterSetting(TransactionCase):

    def test_pay_after_row_is_hidden_but_keeps_its_field(self):
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        rows = etree.fromstring(arch).xpath('//div[@id="self-payment-after"]')

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].get('invisible'), '1')
        self.assertTrue(rows[0].xpath('.//field[@name="pos_self_ordering_pay_after"]'))
