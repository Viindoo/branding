from odoo import api, fields, models


class Users(models.Model):
    _inherit = 'res.users'

    # 'email' is re-declared so this module's catalog translates its label,
    # which core leaves untranslated in some languages.
    notification_type = fields.Selection(
        selection_add=[('email', 'By Emails'), ('inbox', 'In Viindoo')],
        help="How notifications for document messages and system updates are delivered:\n"
             "- By email: Notifications are sent to your email address.\n"
             "- In Viindoo: Notifications appear in your Viindoo inbox.")

    @api.model
    def _sql_error_to_message(self, exc):
        """Name Viindoo in the refusal of an inbox notification for a portal or public user.

        Core words the refusal with the product name and reads it from the constraint record of
        its own module.
        """
        if exc.diag.constraint_name == 'res_users_notification_type':
            return self.env._('Only internal user can receive notifications in Viindoo')
        return super()._sql_error_to_message(exc)
