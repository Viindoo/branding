from odoo import api, models


class AccountMoveSend(models.AbstractModel):
    _inherit = 'account.move.send'

    @api.model
    def _is_applicable_to_company(self, method, company):
        """Offer no sending by post: the postal service is a paid service that Viindoo does not provide."""
        if method == 'snailmail':
            return False
        return super()._is_applicable_to_company(method, company)

    @api.model
    def _get_default_sending_methods(self, move):
        """Never default to sending by post, even for a partner that still holds that preference."""
        methods = super()._get_default_sending_methods(move)
        methods.discard('snailmail')
        return methods or {'email'}
