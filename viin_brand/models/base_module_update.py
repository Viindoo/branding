import ast

from odoo import models
from odoo.fields import Domain

from .ir_module_module import _hide_enterprise_stubs


class BaseModuleUpdate(models.TransientModel):
    _inherit = 'base.module.update'

    def action_module_open(self):
        """Open the list of modules without the Enterprise-only stubs, like the Apps lists.

        Core builds this action in Python, so no action record carries the domain that hides them.
        """
        action = super().action_module_open()
        domain = Domain(ast.literal_eval(action.get('domain') or '[]'))
        action['domain'] = repr(_hide_enterprise_stubs(domain))
        return action
