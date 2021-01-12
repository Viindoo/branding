import os
import odoo
from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def check_file_exists(self, path):
        for odoo_path in odoo.addons.__path__:
            if os.path.exists(odoo_path + path):
                return True
        return False
