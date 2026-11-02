from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    # viin_brand_mail and to_mail_notif_and_email each redefine the whole help text and
    # neither knows the other, so this module, loaded after both, restates it once.
    notification_type = fields.Selection(
        help="Policy on how to handle Chatter notifications:\n"
             "- By Emails: notifications are sent to your email address\n"
             "- In Viindoo: notifications appear in your Viindoo Inbox\n"
             "- By Emails and Inbox: notifications are sent to your email address "
             "and also appear in your Viindoo Inbox")
