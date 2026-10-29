import ast

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.fields import Domain
from odoo.http import request
from odoo.tools import config

# Odoo IAP modules: their rows exist before they are installed, so the guard below knows them by name.
IAP_MODULES = ['iap', 'crm_iap_enrich', 'crm_iap_mine', 'iap_crm', 'iap_mail', 'website_crm_iap_reveal']


def _is_to_buy_condition(condition):
    return condition.field_expr == 'to_buy'


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def _update_domain_for_action(self):
        """Hide the Enterprise-only module stubs (``to_buy``) from the Apps list.

        The condition is ANDed with whatever domain the action already has (website adds one that
        hides themes) and added only once, so reloading data never stacks it.
        """
        action = self.env.ref('base.open_module_tree', raise_if_not_found=False)
        if action:
            domain = Domain(ast.literal_eval(action.domain or '[]'))
            if not any(_is_to_buy_condition(c) for c in domain.iter_conditions()):
                action.domain = repr(Domain('to_buy', '=', False) & domain)
        return action

    @api.model
    def _restore_domain_for_action(self):
        """Drop only the ``to_buy`` condition, leaving the domain other modules put on the action."""
        action = self.env.ref('base.open_module_tree', raise_if_not_found=False)
        if action and action.domain:
            domain = Domain(ast.literal_eval(action.domain)).map_conditions(
                lambda c: Domain.TRUE if _is_to_buy_condition(c) else c,
            )
            action.domain = False if domain.is_true() else repr(domain)

    def button_immediate_install(self):
        self._check_iap_modules_are_not_requested()
        return super().button_immediate_install()

    def _check_iap_modules_are_not_requested(self):
        """Refuse an explicit request, from the user interface, to install an Odoo IAP module.

        Only the records the user asked for are checked: dependencies and auto-installed modules
        are resolved later inside ``button_install`` and are never refused. Installing or updating
        from the command line is not refused, and neither is a script, which has no HTTP request.
        """
        if not request or any(config.get(key) for key in ('init', 'update')):
            return
        refused = self.filtered(lambda module: module.name in IAP_MODULES and module.state == 'uninstalled')
        if refused:
            raise UserError(_(
                "The Odoo IAP modules cannot be installed from the user interface: %s",
                ', '.join(refused.mapped('shortdesc')),
            ))
