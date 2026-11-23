from odoo import api, models, modules, tools

from odoo.addons.iap.tools import iap_tools

from ..tools import is_paid_service, refuse_paid_service


class IapAccount(models.Model):
    _inherit = 'iap.account'

    @api.model
    def get_credits_url(self, service_name, account_token=None):
        """Never ask the IAP of Odoo S.A. for a page to buy credits.

        The request carries the database uuid and the account token.

        :return: an empty URL when the endpoint is a paid service; core's own answer otherwise
        """
        # core answers in test mode without any request
        if self._has_paid_endpoint() and not (tools.config['test_enable'] or modules.module.current_test):
            return ''
        return super().get_credits_url(service_name, account_token=account_token)

    def action_manage(self):
        self._refuse_paid_endpoint()
        return super().action_manage()

    def action_buy_credits(self):
        self._refuse_paid_endpoint()
        return super().action_buy_credits()

    def action_rotate_token(self):
        self._refuse_paid_endpoint()
        return super().action_rotate_token()

    @api.model
    def action_view_my_services(self):
        self._refuse_paid_endpoint()
        return super().action_view_my_services()

    def _get_account_information_from_iap(self):
        """Never ask the IAP of Odoo S.A. for the balance of an account.

        Core reads the balances on every opening of an account and reports an unreachable server
        with a persistent notification, which would blame a service this database never calls.
        """
        if self._has_paid_endpoint():
            return
        return super()._get_account_information_from_iap()

    @api.model
    def _has_paid_endpoint(self):
        return is_paid_service(iap_tools.iap_get_endpoint(self.env))

    @api.model
    def _refuse_paid_endpoint(self):
        if self._has_paid_endpoint():
            refuse_paid_service()
