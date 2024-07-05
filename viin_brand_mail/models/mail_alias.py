from odoo import fields, models


class Alias(models.Model):
    _inherit = 'mail.alias'

    alias_name = fields.Char(help="The name of the email alias, e.g. 'jobs' if you want to catch emails for <jobs@example.viindoo.com>")
    alias_model_id = fields.Many2one(help="The model (Viindoo Document Kind) to which this alias "
                                          "corresponds. Any incoming email that does not reply to an "
                                          "existing record will cause the creation of a new record "
                                          "of this model (e.g. a Project Task)",
                                    )
