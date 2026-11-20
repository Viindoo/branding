import re

from odoo import models
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)
_lt_core = LazyTranslate('l10n_vn_edi_viettel')

CANCEL_MESSAGES_CONTEXT_KEY = 'viin_brand_l10n_vn_edi_viettel_cancel'
REASON_MARK = '[[reason]]'
ERROR_MARK = '[[error]]'

# Plain lookup key: the message core posts when the invoice is cancelled at the provider but not in
# the database, translated through the catalog of the module that owns it; the marks stand for the
# values core interpolates.
CORE_CANCEL_FAILURE = _lt_core(
    'The invoice has been canceled on sinvoice for reason: %(reason)s'
    'But the cancellation in Odoo failed with error: %(error)s',
    reason=REASON_MARK, error=ERROR_MARK)
CANCEL_FAILURE = _lt(
    'The invoice has been canceled on sinvoice for reason: %(reason)s'
    'But the cancellation in Viindoo failed with error: %(error)s',
    reason=REASON_MARK, error=ERROR_MARK)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _l10n_vn_edi_cancel_invoice(self, reason, agreement_document_name, agreement_document_date):
        """Cancel the e-invoice; the failure message of the local cancellation names Viindoo.

        The error of the provider is raised before any message is posted and is left as it is.
        """
        return super(AccountMove, self.with_context(**{CANCEL_MESSAGES_CONTEXT_KEY: True}))._l10n_vn_edi_cancel_invoice(
            reason, agreement_document_name, agreement_document_date)

    def message_post(self, **kwargs):
        body = kwargs.get('body')
        if self.env.context.get(CANCEL_MESSAGES_CONTEXT_KEY) and isinstance(body, str):
            kwargs['body'] = type(body)(self._brand_cancel_failure(body))
        return super().message_post(**kwargs)

    def _brand_cancel_failure(self, body):
        """Return ``body`` with the core failure sentence worded for Viindoo.

        Only a body that is exactly that message is rewritten, and the reason typed by the user and
        the error interpolated in it are kept as they are: they are what was sent to the provider.
        """
        pattern = re.escape(CORE_CANCEL_FAILURE._translate(self.env.lang or 'en_US'))
        pattern = pattern.replace(re.escape(REASON_MARK), '(?P<reason>.*)')
        pattern = pattern.replace(re.escape(ERROR_MARK), '(?P<error>.*)')
        match = re.fullmatch(pattern, body, re.DOTALL)
        if not match:
            return body
        message = CANCEL_FAILURE._translate(self.env.lang or 'en_US')
        return message.replace(REASON_MARK, match['reason']).replace(ERROR_MARK, match['error'])
