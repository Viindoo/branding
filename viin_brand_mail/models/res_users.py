from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    # 'email' is re-declared so this module's catalog translates its label,
    # which core leaves untranslated in some languages.
    notification_type = fields.Selection(
        selection_add=[('email', 'By Emails'), ('inbox', 'In Viindoo')],
        help="Policy on how to handle Chatter notifications:\n"
             "- By Emails: notifications are sent to your email address\n"
             "- In Viindoo: notifications appear in your Viindoo Inbox")
