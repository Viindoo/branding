from unittest.mock import patch

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.account.models.account_move_send import AccountMoveSend


@tagged('post_install', '-at_install')
class TestNoPostSending(TransactionCase):

    def test_sending_by_post_is_never_offered_in_send_and_print(self):
        send = self.env['account.move.send']
        self.assertFalse(send._is_applicable_to_company('snailmail', self.env.company))
        self.assertTrue(send._is_applicable_to_company('email', self.env.company))

    def test_a_partner_preference_for_post_falls_back_to_email(self):
        partner = self.env['res.partner'].create({'name': 'Preference holder'})
        move = self.env['account.move'].create({'move_type': 'out_invoice', 'partner_id': partner.id})
        with patch.object(AccountMoveSend, '_get_default_sending_methods', return_value=['snailmail']):
            self.assertEqual(self.env['account.move.send']._get_default_sending_methods(move), ['email'])

    def test_the_other_default_sending_methods_stay_when_the_preference_is_post(self):
        partner = self.env['res.partner'].create({'name': 'Preference holder'})
        move = self.env['account.move'].create({'move_type': 'out_invoice', 'partner_id': partner.id})
        with patch.object(AccountMoveSend, '_get_default_sending_methods', return_value=['snailmail', 'manual']):
            self.assertEqual(self.env['account.move.send']._get_default_sending_methods(move), ['manual'])

    def test_the_post_choice_is_not_offered_on_the_partner(self):
        field = self.env['res.partner']._fields['invoice_sending_method']
        self.patch(field, 'selection', list(field.selection) + [('snailmail', 'by Post')])
        info = self.env['res.partner'].fields_get(['invoice_sending_method'], attributes=['selection'])
        self.assertNotIn('snailmail', dict(info['invoice_sending_method']['selection']))
        self.assertIn('email', dict(info['invoice_sending_method']['selection']))

    def test_the_post_settings_row_is_hidden(self):
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        rows = etree.fromstring(arch).xpath('//setting[@id="send_invoices_followups"]')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].get('invisible'), '1')
