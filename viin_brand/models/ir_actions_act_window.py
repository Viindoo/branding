from odoo import models

from .res_config_settings import get_settings_app, get_settings_context


class IrActionsAct_Window(models.Model):
    _inherit = 'ir.actions.act_window'

    def _get_action_dict(self):
        """Open the settings on their first app when the app an action names has every setting hidden."""
        result = super()._get_action_dict()
        if result.get('res_model') != 'res.config.settings':
            return result
        app = get_settings_app(result.get('context'))
        # sudo(False): the app is hidden or not as the user who opens the action sees the settings
        if app and app in self.env['res.config.settings'].sudo(False)._get_unusable_apps():
            context = get_settings_context(result['context'])
            del context['module']
            result['context'] = repr(context)
        return result
