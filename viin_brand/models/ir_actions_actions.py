from odoo import api, models


class IrActionsActions(models.Model):
    _inherit = 'ir.actions.actions'

    @api.model
    def _get_hidden_binding_xmlids(self):
        """Return the XML ids of the actions that are kept out of the Action menu of every model.

        An id that does not resolve (the module that owns it is not installed) is ignored. Branding
        modules extend the list for the actions of their own app; the actions stay reachable by
        their id.

        :return: a list of fully qualified XML ids
        """
        return []

    @api.model
    def get_bindings(self, model_name):
        bindings = super().get_bindings(model_name)
        hidden_ids = set()
        for xmlid in self._get_hidden_binding_xmlids():
            hidden_ids.update((self.env.ref(xmlid, raise_if_not_found=False) or self.browse()).ids)
        if not hidden_ids:
            return bindings
        result = {}
        for binding_type, actions in bindings.items():
            kept = [action for action in actions if action['id'] not in hidden_ids]
            if kept:
                result[binding_type] = kept
        return result
