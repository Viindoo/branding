from odoo import models


class SnailmailLetter(models.Model):
    _inherit = 'snailmail.letter'

    def _get_error_message(self, error):
        # The credits link goes to the Odoo-hosted IAP service, so the text names the IAP account, not Viindoo.
        if error == 'TRIAL_ERROR':
            link = self.env['iap.account'].get_credits_url(service_name='snailmail')
            return self.env._(
                'You don\'t have an IAP account registered for this service.<br>'
                'Please go to your <a href=%s target="new">IAP account</a> to claim your free credits.',
                link,
            )
        return super()._get_error_message(error)
