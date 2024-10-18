from markupsafe import Markup
from odoo import models, _


class MassMailing(models.Model):
    _inherit = 'mailing.mailing'

    def action_redirect_to_leads_and_opportunities(self):
        res = super().action_redirect_to_leads_and_opportunities()
        text = _("Leads") if self.use_leads else _("Opportunities")
        helper_header = _("No %s yet!", text)
        helper_message = _("Note that Viindoo cannot track replies if they are sent towards email addresses to this database.")
        res.update({
            'help': Markup('<p class="o_view_nocontent_smiling_face">%s</p><p>%s</p>') % (
                helper_header, helper_message,
            ),
        })
        return res
