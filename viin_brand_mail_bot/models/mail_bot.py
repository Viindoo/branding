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
                if self._is_help_requested(body) or odoobot_state == 'idle':
                    return Markup(_("Unfortunately, I'm just a bot 😞 I don't understand! If you need help discovering our product, please check "
                             "<a href=\"https://www.viindoo.com/documentation\" target=\"_blank\">our documentation</a> or "
                             "<a href=\"https://www.viindoo.com/slides\" target=\"_blank\">our videos</a>."))
                elif odoobot_state == 'onboarding_attachement' and values.get("attachment_ids"):
                    self.env.user.odoobot_state = "idle"
                    self.env.user.odoobot_failed = False
                    return Markup(_("I am a simple bot, but if that's a dog, he is the cutest 😊 <br/>Congratulations, you finished this tour. You can now <b>close this conversation</b> or start the tour again with typing <span class=\"o_odoobot_command\">start the tour</span>. Enjoy discovering Viindoo!"))
                # Actually this one should be in im_livechat_mail_bot
                elif odoobot_state == "onboarding_canned" and self.env.context.get("canned_response_ids"):
                    self.env.user.odoobot_failed = False
                    self.env.user.odoobot_state = "idle"
                    return Markup(_("Good, you can customize canned responses in the live chat application.<br/><br/><b>It's the end of this overview</b>, you can now <b>close this conversation</b> or start the tour again with typing <span class=\"o_odoobot_command\">start the tour</span>. Enjoy discovering Viindoo!"))

            return super(MailBot, self)._get_answer(record, body, values, command)
