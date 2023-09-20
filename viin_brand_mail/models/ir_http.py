from odoo import models


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        """Override to change support_url from `https://www.odoo.com/buy` to `https://viindoo.com/pricing`
        """
        session_info = super().session_info()
        session_info['support_url'] = 'https://viindoo.com/pricing'
        return session_info
