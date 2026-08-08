from markupsafe import Markup

from odoo import models, _
from odoo.tools import config


class MailBot(models.AbstractModel):
    _inherit = 'mail.bot'

    @staticmethod
    def _get_style_dict():
        return {
            "new_line": Markup("<br>"),
            "bold_start": Markup("<b>"),
            "bold_end": Markup("</b>"),
            "command_start": Markup("<span class='o_odoobot_command'>"),
            "command_end": Markup("</span>"),
            "document_link_start": Markup("<a href='https://www.viindoo.com/documentation' target='_blank'>"),
            "document_link_end": Markup("</a>"),
            "slides_link_start": Markup("<a href='https://www.viindoo.com/slides' target='_blank'>"),
            "slides_link_end": Markup("</a>"),
            "paperclip_icon": Markup("<i class='fa fa-paperclip' aria-hidden='true'/>"),
        }

    def _get_answer(self, channel, body, values, command=False):
        if config.get('test_enable', False):
            return super()._get_answer(channel, body, values, command)
        odoobot = self.env.ref("base.partner_root")
        odoobot_state = self.env.user.odoobot_state

        if channel.channel_type == "chat" and odoobot in channel.channel_member_ids.partner_id:
            # Override messages containing "OdooBot" or "Odoo" brand name
            if odoobot_state == 'onboarding_command' and command == 'help':
                self.env.user.odoobot_state = "onboarding_ping"
                self.env.user.odoobot_failed = False
                return self.env._(
                    "Wow you are a natural!%(new_line)sPing someone with @username to grab their "
                    "attention. %(bold_start)sTry to ping me using%(bold_end)s "
                    "%(command_start)s@ViindooBot%(command_end)s in a sentence.",
                    **self._get_style_dict()
                )
            if odoobot_state == "onboarding_canned" and self.env.context.get("canned_response_ids"):
                source = _("Thanks")
                self.env["mail.canned.response"].search([
                    ("create_uid", "=", self.env.user.id),
                    ("source", "=", source),
                ]).unlink()
                self.env.user.odoobot_failed = False
                self.env.user.odoobot_state = "idle"
                return [
                    self.env._(
                        "Great! You can customize %(bold_start)scanned responses%(bold_end)s in the Discuss app.",
                        **self._get_style_dict(),
                    ),
                    self.env._(
                        "That's the end of this overview. You can %(bold_start)sclose this conversation%(bold_end)s or type "
                        "%(command_start)sstart the tour%(command_end)s to see it again. Enjoy discovering Viindoo!",
                        **self._get_style_dict(),
                    ),
                ]
            # Failure case: user didn't ping the bot (but not when asking for help)
            if (odoobot_state == 'onboarding_ping'
                    and odoobot.id not in values.get("partner_ids", [])
                    and not self._is_help_requested(body)):
                self.env.user.odoobot_failed = True
                return self.env._(
                    "Sorry, I am not listening. To get someone's attention, %(bold_start)sping "
                    "him%(bold_end)s. Write %(command_start)s@ViindooBot%(command_end)s and select"
                    " me.",
                    **self._get_style_dict()
                )

        return super()._get_answer(channel, body, values, command)
