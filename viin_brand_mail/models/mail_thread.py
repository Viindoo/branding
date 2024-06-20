from odoo import models


class MailThread(models.AbstractModel):
    _name = 'mail.thread'

    def _notify_by_web_push_prepare_payload(self, message, msg_vals=False):
        payload = super()._notify_by_web_push_prepare_payload(message, msg_vals)
        if 'options' in payload and 'icon' in payload['options'] and 'odoo-icon-192x192.png' in payload['options']['icon']:
            payload['options']['icon'] = '/viin_brand_mail/static/img/viindoo_app_icon.png'
        return payload
