import re

from odoo import api, models
from odoo.tools.translate import LazyTranslate

from odoo.addons.viin_brand.tools import PRODUCT_NAME

# The subtitle core gives the account-created email of a new user; equal to a lazy translation of
# the same source in the same module, whatever the language it is rendered in.
CORE_WELCOME_SUBTITLE = LazyTranslate('auth_signup')('Welcome to Odoo')


class MailRenderMixin(models.AbstractModel):
    _inherit = 'mail.render.mixin'

    @api.model
    def _render_encapsulate(self, layout_xmlid, html, add_context=None, context_record=None):
        """Name the product in the welcome subtitle of the email sent to a new user.

        Core builds the subtitle in Python and translates it with its own catalog, so the product
        name is replaced in the text that is rendered, in the language of the recipient.
        """
        subtitles = self.env.context.get('email_notification_subtitles')
        if subtitles and CORE_WELCOME_SUBTITLE in subtitles:
            subtitles = [
                re.sub(r'\bOdoo\b', PRODUCT_NAME, str(subtitle)) if subtitle == CORE_WELCOME_SUBTITLE else subtitle
                for subtitle in subtitles
            ]
            self = self.with_context(email_notification_subtitles=subtitles)
        return super()._render_encapsulate(
            layout_xmlid, html, add_context=add_context, context_record=context_record)
