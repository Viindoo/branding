import re

from odoo import api, models

# The models the invitation, reminder and update mails of the calendar are rendered for.
CALENDAR_MAIL_MODELS = ('calendar.attendee', 'calendar.event')
CORE_VIDEOCALL_NAME = re.compile(r'\bOdoo Discuss\b')


class MailRenderMixin(models.AbstractModel):
    _inherit = 'mail.render.mixin'

    @api.model
    def _render_template_postprocess(self, model, rendered):
        """Name the Viindoo video conference in the meeting mails, in whatever language they are sent.

        The stored body of the mail template stays as core wrote it; the product name is replaced
        in what is rendered from it.
        """
        rendered = super()._render_template_postprocess(model, rendered)
        if model in CALENDAR_MAIL_MODELS:
            for res_id, body in rendered.items():
                rendered[res_id] = type(body)(CORE_VIDEOCALL_NAME.sub('Viindoo Discuss', body))
        return rendered
