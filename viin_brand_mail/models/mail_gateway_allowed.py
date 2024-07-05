from markupsafe import Markup
from odoo import _, api, models


class MailGatewayAllowed(models.Model):
    _inherit = 'mail.gateway.allowed'

    @api.model
    def get_empty_list_help(self, help_message):
        """
        Completely overwrite
        """
        get_param = self.env['ir.config_parameter'].sudo().get_param
        LOOP_MINUTES = int(get_param('mail.gateway.loop.minutes', 120))
        LOOP_THRESHOLD = int(get_param('mail.gateway.loop.threshold', 20))

        return Markup(_('''
            <p class="o_view_nocontent_smiling_face">
                Add addresses to the Allowed List
            </p><p>
                To protect you from spam and reply loops, Viindoo automatically blocks emails
                coming to your gateway past a threshold of <b>%(threshold)i</b> emails every <b>%(minutes)i</b>
                minutes. If there are some addresses from which you need to receive very frequent
                updates, you can however add them below and Viindoo will let them go through.
            </p>''')) % {
            'threshold': LOOP_THRESHOLD,
            'minutes': LOOP_MINUTES,
        }
