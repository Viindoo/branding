from odoo import models, fields


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    from_filter = fields.Char(
        help="Comma-separated list of addresses or domains for which this server can be used.\n"
             "e.g.: 'notification@viindoo.com' or 'viindoo.com")
