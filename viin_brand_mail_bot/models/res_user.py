from markupsafe import Markup

from odoo import fields, models
from odoo.tools.translate import LazyTranslate

_core_lt = LazyTranslate('mail_bot')


class Users(models.Model):
    _inherit = 'res.users'

    odoobot_state = fields.Selection(string='ViindooBot Status')

    def _init_odoobot(self):
        # Core posts the message inline with no hook for the product name, so super() cannot be
        # used; the sentences are read from the catalog of core, which holds every language.
        self.ensure_one()
        lang = self.env.lang or 'en_US'
        odoobot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
        channel = self.env['discuss.channel']._get_or_create_chat([odoobot_id, self.partner_id.id])
        rebrand = self.env['mail.bot']._rebrand_answer
        message = Markup("%s<br/>%s<br/><b>%s</b>") % tuple(
            rebrand(sentence._translate(lang))
            for sentence in (
                _core_lt("Hello 👋"),
                _core_lt(
                    "Odoo's Discuss application helps employees collaborate efficiently. "
                    "I'm here to help you explore its features."
                ),
                _core_lt("Go ahead - Try sending me an emoji 😊"),
            )
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
