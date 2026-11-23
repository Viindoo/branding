from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDigestTip(TransactionCase):

    def test_configurable_products_tip_names_viindoo_not_odoo(self):
        tip = self.env.ref('sale_management.digest_tip_sale1_management_0').with_context(lang='en_US')
        for text in (tip.name, tip.tip_description):
            self.assertIn('Viindoo', text)
            self.assertNotIn('Odoo', text)
