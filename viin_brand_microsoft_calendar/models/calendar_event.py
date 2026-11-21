from odoo import models
from odoo.exceptions import UserError

from odoo.addons.viin_brand.tools import debrand_exception


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def _check_organizer_validation(self, sender_user, partner_included):
        """Raise the organizer errors of the Outlook synchronisation with the Viindoo name."""
        try:
            return super()._check_organizer_validation(sender_user, partner_included)
        except UserError as error:
            raise debrand_exception(error) from None

    def _forbid_recurrence_update(self):
        """Raise the recurrence update error of the Outlook synchronisation with the Viindoo name."""
        try:
            return super()._forbid_recurrence_update()
        except UserError as error:
            raise debrand_exception(error) from None

    def _ensure_attendees_have_email(self):
        """Raise the missing attendee email error of the Outlook synchronisation with the Viindoo name."""
        try:
            return super()._ensure_attendees_have_email()
        except UserError as error:
            raise debrand_exception(error) from None
