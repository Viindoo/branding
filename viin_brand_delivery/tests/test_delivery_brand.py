from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDeliveryEnterpriseOffer(TransactionCase):

    def test_carrier_form_offers_no_more_providers_button(self):
        arch = self.env['delivery.carrier'].get_view(
            view_id=self.env.ref('delivery.view_delivery_carrier_form').id, view_type='form')['arch']
        self.assertFalse(etree.fromstring(arch).xpath("//button[@name='install_more_provider']"))

    def test_more_providers_action_has_no_enterprise_offer(self):
        action = self.env['delivery.carrier'].install_more_provider()
        self.assertEqual(action['res_model'], 'ir.module.module')
        self.assertNotIn('help', action)
