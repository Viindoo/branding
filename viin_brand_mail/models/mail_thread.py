from odoo import models, tools


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_by_web_push_prepare_payload(self, message, msg_vals=False, force_record_name=False):
        payload = super()._notify_by_web_push_prepare_payload(
            message, msg_vals=msg_vals, force_record_name=force_record_name,
        )
        if not tools.config.get('test_enable', False) and 'options' in payload and 'icon' in payload['options'] and 'odoo-icon-192x192.png' in payload['options']['icon']:
            payload['options']['icon'] = '/viin_brand_common/static/img/viindoo-icon-192x192.png'
        return payload
