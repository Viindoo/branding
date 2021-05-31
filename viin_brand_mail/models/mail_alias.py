from odoo import fields, models

class Alias(models.Model):
    _inherit = 'mail.alias'

    alias_name = fields.Char(help="The name of the email alias, e.g. 'jobs' if you want to catch emails for <jobs@example.viindoo.com>")
