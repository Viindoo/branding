from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSmsBridge(TransactionCase):

    def test_sms_is_always_installed_with_a_way_to_send_that_is_not_odoo(self):
        modules = self.env['ir.module.module'].search([('name', 'in', ('sms', 'sms_twilio'))])
        self.assertEqual(set(modules.mapped('state')), {'installed'})
