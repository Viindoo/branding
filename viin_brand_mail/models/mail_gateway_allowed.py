from markupsafe import Markup
from odoo import _, api, models


class MailGatewayAllowed(models.Model):
    _inherit = 'mail.gateway.allowed'

    @api.model
    def get_empty_list_help(self, help_message):
        """Return the empty-list help of the allowed list, naming Viindoo.

        :param help_message: the help message of the action
        :return: the help markup
        """
        # sudo: system parameters of the loop guard; the user only reads the thresholds shown in the help
        get_int = self.env['ir.config_parameter'].sudo().get_int
        loop_minutes = get_int('mail.gateway.loop.minutes') or 120
        loop_threshold = get_int('mail.gateway.loop.threshold') or 20

        return Markup(_('''
            <p class="o_view_nocontent_smiling_face">
                Add addresses to the Allowed List
            </p><p>
                To protect you from spam and reply loops, Viindoo automatically blocks emails
                coming to your gateway past a threshold of <b>%(threshold)i</b> emails every <b>%(minutes)i</b>
                minutes. If there are some addresses from which you need to receive very frequent
                updates, you can however add them below and Viindoo will let them go through.
            </p>''')) % {
            'threshold': loop_threshold,
            'minutes': loop_minutes,
        }
