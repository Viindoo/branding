from markupsafe import escape

from odoo import models
from odoo.tools.translate import LazyTranslate

from odoo.addons.viin_brand.tools import PRODUCT_NAME

_core_lt = LazyTranslate('mail')
CORE_RECORDING_SENTENCE = _core_lt("Your meeting recording is available in Odoo.")


class MailCallArtifact(models.Model):
    _inherit = 'mail.call.artifact'

    def _send_recording_available_email(self):
        """Name Viindoo in the sentence of the email that announces a recording.

        Core words the sentence with the product name inside the body it queues, in the language
        of the recipient and with no hook, so the sentence is replaced in the queued mails of the
        artifacts. It is read from the catalog of core, which holds every language.
        """
        super()._send_recording_available_email()
        # sudo: mail.mail - core queues these mails with sudo, for the starters of the recordings
        mails = self.env['mail.mail'].sudo().search([
            ('model', '=', self._name),
            ('res_id', 'in', self.ids),
            ('state', '=', 'outgoing'),
        ])
        for mail in mails:
            sentence = str(escape(CORE_RECORDING_SENTENCE._translate(mail.recipient_ids[:1].lang or 'en_US')))
            branded = sentence.replace('Odoo', PRODUCT_NAME)
            if branded != sentence and sentence in mail.body_html:
                mail.body_html = mail.body_html.replace(sentence, branded)
