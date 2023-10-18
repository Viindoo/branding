from odoo import models, api, tools


class Module(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def get_apps_server(self):
        """
        Completely overide to change the apps_server
        as well as return the modules of the client instance
        """
        # TODO: in v17 or master+ find a way to avoid changing return type of this method
        modules = self.search_read([], ['name', 'installed_version'])
        return tools.config.get('apps_server', 'https://viindoo.com/apps'), modules
