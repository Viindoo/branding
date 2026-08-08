from markupsafe import Markup

from odoo import models, fields


class Users(models.Model):
    _inherit = 'res.users'

    # Override to branding
    odoobot_state = fields.Selection(string='ViindooBot Status')

    def _init_odoobot(self):
        # Full reimplementation of mail_bot's res.users._init_odoobot(): core
        # builds the whole onboarding Markup inline from 3 hardcoded _(...)
        # pieces (odoo/addons/mail_bot/models/res_users.py) with no override
        # hook to intercept just the branded sentence, so super() cannot be
        # used here - only the middle sentence is re-branded to Viindoo.
        self.ensure_one()
        odoobot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
        channel = self.env['discuss.channel']._get_or_create_chat([odoobot_id, self.partner_id.id])
        message = Markup("%s<br/>%s<br/><b>%s</b> <span class=\"o_odoobot_command\">:)</span>") % (
            self.env._("Hello,"),
            self.env._(
                "Viindoo's chat helps employees collaborate efficiently. "
                "I'm here to help you discover its features."
            ),
            self.env._("Try to send me an emoji"),
        )
        channel.sudo().message_post(
            author_id=odoobot_id,
            body=message,
            message_type="comment",
            silent=True,
            subtype_xmlid="mail.mt_comment",
        )
        self.sudo().odoobot_state = 'onboarding_emoji'
        return channel
