from odoo import models


class CrmRevealRule(models.Model):
    _inherit = 'crm.reveal.rule'

    def _match_url(self, website_id, url, country_code, state_code, rules_excluded):
        """Match no rule: while the service is switched off no visit is recorded.

        The rules keep the state the users gave them, and they match again when this module is
        uninstalled.
        """
        return []
