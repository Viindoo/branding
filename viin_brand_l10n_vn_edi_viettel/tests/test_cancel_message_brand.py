from unittest.mock import patch

from odoo import fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.tests import tagged

ACCOUNT_MOVE = 'odoo.addons.l10n_vn_edi_viettel.models.account_move'


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestCancelMessageBrand(AccountTestInvoicingCommon):

    @classmethod
    @AccountTestInvoicingCommon.setup_country('vn')
    def setUpClass(cls):
        super().setUpClass()
        template = cls.env['l10n_vn_edi_viettel.sinvoice.template'].create({
            'name': '1/001',
            'template_invoice_type': '1',
        })
        symbol = cls.env['l10n_vn_edi_viettel.sinvoice.symbol'].create({
            'name': 'K24TUT',
            'invoice_template_id': template.id,
        })
        cls.env['ir.default'].set(
            'res.partner', 'l10n_vn_edi_symbol', symbol.id, company_id=cls.env.company.id)
        cls.env.company.write({'vat': '0100109106-506', 'country_id': cls.env.ref('base.vn').id})
        cls.invoice = cls.init_invoice(move_type='out_invoice', products=cls.product_a, post=True)
        cls.invoice.write({
            'l10n_vn_edi_invoice_number': 'K24TUT1',
            'l10n_vn_edi_issue_date': fields.Datetime.now(),
            'l10n_vn_edi_invoice_state': 'sent',
        })

    def _cancel(self, lock_error=None, reason='Unwanted'):
        with patch(ACCOUNT_MOVE + '._l10n_vn_edi_send_request', return_value=(None, None)), \
                patch(ACCOUNT_MOVE + '.AccountMove._l10n_vn_edi_get_access_token', return_value=('token', None)), \
                patch('odoo.addons.account.models.account_move.AccountMove._check_fiscal_lock_dates',
                      side_effect=lock_error):
            self.invoice._l10n_vn_edi_cancel_invoice(reason, 'N/A', fields.Datetime.now())
        return self.invoice.message_ids[0].body

    def test_local_cancellation_failure_message_names_viindoo_not_odoo(self):
        body = str(self._cancel(lock_error=UserError('The period is locked')))
        self.assertIn('The period is locked', body)
        self.assertNotRegex(body, r'\bOdoo\b')
        self.assertIn('cancellation in Viindoo failed', body)

    def test_the_reason_typed_by_the_user_is_posted_as_typed_when_the_cancellation_succeeds(self):
        body = str(self._cancel(reason='Entered on Odoo by mistake'))
        self.assertIn('Entered on Odoo by mistake', body)

    def test_the_reason_and_the_error_of_a_failed_local_cancellation_are_kept_as_they_are(self):
        body = str(self._cancel(lock_error=UserError('Locked by Odoo until June'), reason='Entered on Odoo by mistake'))
        self.assertIn('Entered on Odoo by mistake', body)
        self.assertIn('Locked by Odoo until June', body)
        self.assertIn('cancellation in Viindoo failed', body)
        self.assertNotIn('cancellation in Odoo failed', body)

    def test_messages_posted_outside_the_cancellation_are_untouched(self):
        self.invoice.message_post(body='Sent through Odoo')
        self.assertIn('Sent through Odoo', str(self.invoice.message_ids[0].body))
