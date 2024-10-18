from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    alias_domain_id = fields.Many2one(help="If you have setup a catch-all email domain redirected to the Viindoo server,"
        " enter the domain name here.")
