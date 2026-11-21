from odoo import models


class MailingMailing(models.Model):
    _inherit = 'mailing.mailing'

    def action_put_in_queue(self):
        self._raise_if_sms_not_configured()
        return super().action_put_in_queue()

    def action_schedule(self):
        self._raise_if_sms_not_configured()
        return super().action_schedule()

    def action_send_mail(self, res_ids=None):
        self._raise_if_sms_not_configured()
        return super().action_send_mail(res_ids=res_ids)

    def _raise_if_sms_not_configured(self):
        """Stop the manual send of an SMS campaign when the company has no Twilio account.

        A cron or an automation (the winner of an A/B test, for one) is never stopped: the SMS it
        queues fail one by one with the not-configured sentence.

        :raises RedirectWarning: for an administrator, with a button that opens the settings
        :raises UserError: for any other user, with the same sentence
        """
        if self.env.su or self.env.context.get('cron_id'):
            return
        if self.filtered(lambda mailing: mailing.mailing_type == 'sms'):
            self.env.company._raise_if_sms_not_configured()
