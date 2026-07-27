from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    notification_type = fields.Selection(
        selection_add=[('email',), ('inbox', 'Handle in Viindoo')],
        help="Policy on how to handle Chatter notifications:\n"
             "- By Emails: notifications are sent to your email address\n"
             "- In Viindoo: notifications appear in your Viindoo Inbox")
