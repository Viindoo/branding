from odoo import api, models


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def _get_apps_actions(self):
        """Add the Apps list of the website to the lists that hide the Enterprise-only stubs."""
        website_apps = self.env.ref('website.action_website_add_features', raise_if_not_found=False)
        return super()._get_apps_actions() | (website_apps or self.env['ir.actions.act_window'])
