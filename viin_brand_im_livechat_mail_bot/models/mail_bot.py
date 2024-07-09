import threading
from markupsafe import Markup

from odoo import models, _


class MailBot(models.AbstractModel):
    _inherit = 'mail.bot'

    def _get_answer(self, record, body, values, command=False):
        test_mode = getattr(threading.current_thread(), 'testing', False) or self.env.registry.in_test_mode()
        if test_mode:
            return super(MailBot, self)._get_answer(record, body, values, command)
        else:
            odoobot_state = self.env.user.odoobot_state
            if self._is_bot_in_private_channel(record):
                # help message
                if odoobot_state == "onboarding_canned" and self.env.context.get("canned_response_ids"):
                    self.env.user.odoobot_failed = False
                    self.env.user.odoobot_state = "idle"
                    return Markup(_("Good, you can customize canned responses in the live chat application.<br/><br/><b>It's the end of this overview</b>, you can now <b>close this conversation</b> or start the tour again with typing <span class=\"o_odoobot_command\">start the tour</span>. Enjoy discovering Viindoo!"))

            return super(MailBot, self)._get_answer(record, body, values, command)
