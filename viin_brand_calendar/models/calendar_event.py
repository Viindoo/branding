import re

from odoo import models

# An alarm without a name makes core fall back to its own product name as the alarm description.
_ALARM_DESCRIPTION_FALLBACK = re.compile(rb'(BEGIN:VALARM\r\n(?:(?!END:VALARM)[\s\S])*?DESCRIPTION:)Odoo(\r\n)')


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def _get_ics_file(self):
        """Give the alarms of the invitation files the Viindoo name where core would write its own."""
        return {
            meeting_id: _ALARM_DESCRIPTION_FALLBACK.sub(rb'\1Viindoo\2', ics)
            for meeting_id, ics in super()._get_ics_file().items()
        }
