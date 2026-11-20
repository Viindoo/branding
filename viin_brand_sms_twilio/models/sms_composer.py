from odoo import api, models


class SmsComposer(models.TransientModel):
    _inherit = 'sms.composer'

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('viin_brand_sms_twilio_test'):
            for vals in vals_list:
                if vals.get('body'):
                    vals['body'] = vals['body'].replace('Odoo', 'Viindoo')
        return super().create(vals_list)

    def action_send_sms(self):
        if not self.env.context.get('viin_brand_sms_automated'):
            self._get_sending_companies()._raise_if_sms_not_configured()
        return super().action_send_sms()

    def _get_sending_companies(self):
        """Return the companies that the SMS of this composer are sent with.

        A message posted on a record goes out with the company of that record; any other SMS goes
        out with the current company.
        """
        self.ensure_one()
        companies = self.env['res.company']
        if self.composition_mode == 'comment':
            records = self._get_records()
            if records:
                companies = companies.union(*records._mail_get_companies(default=self.env.company).values())
        return companies or self.env.company
