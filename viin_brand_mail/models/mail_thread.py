from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_by_web_push_prepare_payload(self, message, force_record_name=False):
        payload = super()._notify_by_web_push_prepare_payload(message, force_record_name=force_record_name)
        # Core falls back to the Odoo icon when the notification has no author (e.g. a guest
        # sender). The 192x192 icon of viin_brand is used: the app icon of this module is only 95x95.
        icon = (payload.get('options') or {}).get('icon') or ''
        if 'odoo-icon-192x192.png' in icon:
            payload['options']['icon'] = '/viin_brand/static/img/viindoo-icon-192x192.png'
        return payload
