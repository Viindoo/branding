from urllib.parse import urlsplit

from odoo import models

# The Viindoo page of the documentation on trusted bank accounts, which the phishing warnings link to.
# It repeats the entry of the documentation map of viin_brand, a JavaScript table that the server cannot read.
TRUSTED_ACCOUNTS_DOCUMENTATION_URL = (
    'https://viindoo.com/documentation/20.0/applications/finance/accounting-and-invoicing/'
    'account-payables/vendor-payments/how-to-trust-a-vendor-bank-account.html'
)


def _is_odoo_link(action):
    """Return whether ``action`` opens a page of the site of Odoo."""
    if action.get('type') != 'ir.actions.act_url':
        return False
    host = urlsplit(action.get('url') or '').hostname or ''
    return host == 'odoo.com' or host.endswith('.odoo.com')


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _compute_phishing_warnings(self):
        """Send the "Learn more" link of a phishing warning to the documentation of Viindoo."""
        super()._compute_phishing_warnings()
        for account in self:
            # the warnings of the accounts share one action dict, so the branded ones are copies
            account.phishing_warnings = {
                key: {**warning, 'action': {**warning['action'], 'url': TRUSTED_ACCOUNTS_DOCUMENTATION_URL}}
                if _is_odoo_link(warning.get('action') or {}) else warning
                for key, warning in (account.phishing_warnings or {}).items()
            }
