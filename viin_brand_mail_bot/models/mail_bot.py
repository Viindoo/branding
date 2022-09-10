import threading

from odoo import models, _

class MailBot(models.AbstractModel):
    _inherit = 'mail.bot'
    
    def _get_answer(self, record, body, values, command=False):
        test_mode = getattr(threading.currentThread(), 'testing', False) or self.env.registry.in_test_mode()
        res = super(MailBot,self)._get_answer(record, body, values, command)
        if test_mode:
            return res
        else:
            odoobot_state = self.env.user.odoobot_state
            if self._is_bot_in_private_channel(record):
                # help message
                if self._is_help_requested(body) or odoobot_state == 'idle':
                    return _("Unfortunately, I'm just a bot 😞 I don't understand! If you need help discovering our product, please check "
                             "<a href=\"https://www.viindoo.com/documentation\" target=\"_blank\">our documentation</a> or "
                             "<a href=\"https://www.viindoo.com/slides\" target=\"_blank\">our videos</a>.")
                return res
