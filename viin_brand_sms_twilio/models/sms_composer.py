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
