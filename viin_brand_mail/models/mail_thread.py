from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_by_web_push_prepare_payload(self, message, msg_vals=False, force_record_name=False):
        payload = super()._notify_by_web_push_prepare_payload(message, msg_vals, force_record_name=force_record_name)
        # De-brand the anonymous web-push icon: core falls back to the Odoo mascot
        # when the notification has no author (e.g. a guest sender), so substitute
        # the Viindoo app icon.
        #
        # This substitution is UNCONDITIONAL - the production path has exactly ONE
        # shape and never branches on test configuration. A previous version gated
        # it on `not tools.config.get('test_enable')`, which inverted the risk: the
        # de-brand would have silently switched OFF on any server started with
        # `--test-enable`, and the real production branch was exercised by no test
        # at all.
        #
        # The one core test whose assertion this invalidates -
        # `test_mail.tests.test_mail_push.TestWebPushNotification
        # .test_notify_by_push_channel` (it asserts the literal
        # `odoo-icon-192x192.png` for a guest sender) - is not neutered: this
        # module's `post_load()` wraps it so the de-brand below is bypassed for the
        # duration of that one test, leaving all 13 of its assertions running against
        # core's own behaviour. `tests/test_web_push_icon_debrand.py` protects the
        # de-brand itself.
        #
        # Target asset: `viin_brand_common/static/img/viindoo-icon-192x192.png`, not this
        # module's own `static/img/viindoo_app_icon.png` - the latter is 95x95px (verified
        # on disk), not the 192x192 the core string being replaced names, so it is not the
        # size-correct swap; viin_brand_mail hard-depends on viin_brand_common.
        icon = (payload.get('options') or {}).get('icon') or ''
        if 'odoo-icon-192x192.png' in icon:
            payload['options']['icon'] = '/viin_brand_common/static/img/viindoo-icon-192x192.png'
        return payload
