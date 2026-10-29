import ast

from odoo import api, fields, models
from odoo.fields import Domain


def _is_to_buy_condition(condition):
    return condition.field_expr == 'module_to_buy'


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    capture_manually = fields.Boolean(
        help="Capture the amount from the system, when the delivery is completed.\n"
        "Use this if you want to charge your customers cards only when\n"
        "you are sure you can ship the goods to them.")

    support_refund = fields.Selection(
        help="Refund is a feature allowing to refund customers directly from the payment in the system.")

    @api.model
    def _update_domain_for_action_payment_provider(self):
        """Hide the Enterprise-only payment providers (``module_to_buy``) from the providers list.

        Added only once, so reloading data never stacks the condition.
        """
        action = self.env.ref('payment.action_payment_provider', raise_if_not_found=False)
        if action:
            domain = Domain(ast.literal_eval(action.domain or '[]'))
            if not any(_is_to_buy_condition(c) for c in domain.iter_conditions()):
                action.domain = repr(Domain('module_to_buy', '=', False) & domain)
        return action

    @api.model
    def _restore_domain_for_action_payment_provider(self):
        """Drop only the ``module_to_buy`` condition, leaving any domain other modules put on the action."""
        action = self.env.ref('payment.action_payment_provider', raise_if_not_found=False)
        if action and action.domain:
            domain = Domain(ast.literal_eval(action.domain)).map_conditions(
                lambda c: Domain.TRUE if _is_to_buy_condition(c) else c,
            )
            action.domain = False if domain.is_true() else repr(domain)
