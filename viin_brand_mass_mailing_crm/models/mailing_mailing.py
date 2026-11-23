from markupsafe import Markup

from odoo import models, _
from odoo.tools.translate import LazyTranslate

_core_lt = LazyTranslate('mass_mailing_crm')


class MassMailing(models.Model):
    _inherit = 'mailing.mailing'

    def action_redirect_to_leads_and_opportunities(self):
        res = super().action_redirect_to_leads_and_opportunities()
        text = _("Leads") if self.use_leads else _("Opportunities")
        helper_header = _("No %s yet!", text)
        helper_message = _(
            "Note that Viindoo cannot track replies if they are sent towards email addresses to this database."
        )
        res.update({
            'help': Markup('<p class="o_view_nocontent_smiling_face">%s</p><p>%s</p>') % (
                helper_header, helper_message,
            ),
        })
        return res

    def _prepare_statistics_email_values(self):
        values = super()._prepare_statistics_email_values()
        # Mass Mailing Sales renames the kpi_name of the lead block, so the block that carries the
        # link is found by its tip, not by its name.
        for kpi in values['kpi_data']:
            if 'odoo.com' in str(kpi.get('kpi_tip') or ''):
                # the tip of core ends with a link to the documentation of Odoo: only its sentence is kept
                kpi['kpi_tip'] = _core_lt(
                    "Looking to turn your mailings into leads? Use your sales team's email as the reply-to address."
                )._translate(self.env.lang or 'en_US')
        return values
