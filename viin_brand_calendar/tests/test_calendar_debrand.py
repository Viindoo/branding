# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCalendarDebrand(TransactionCase):

    def test_invitation_alarm_without_a_name_is_described_as_viindoo(self):
        alarm = self.env["calendar.alarm"].create(
            {"name": "", "alarm_type": "notification", "duration": 10, "interval": "minutes"},
        )
        event = self.env["calendar.event"].create({
            "name": "Kick-off",
            "start": "2026-03-02 09:00:00",
            "stop": "2026-03-02 10:00:00",
            "alarm_ids": [(6, 0, alarm.ids)],
        })

        ics = event._get_ics_file()[event.id].decode()

        self.assertIn("DESCRIPTION:Viindoo\r\n", ics)
        self.assertNotIn("DESCRIPTION:Odoo", ics)

    def test_invitation_alarm_keeps_the_name_it_has(self):
        alarm = self.env["calendar.alarm"].create(
            {"name": "Ten minutes before", "alarm_type": "notification", "duration": 10, "interval": "minutes"},
        )
        event = self.env["calendar.event"].create({
            "name": "Kick-off",
            "start": "2026-03-02 09:00:00",
            "stop": "2026-03-02 10:00:00",
            "alarm_ids": [(6, 0, alarm.ids)],
        })

        ics = event._get_ics_file()[event.id].decode()

        self.assertIn("DESCRIPTION:Ten minutes before", ics)

    def test_videocall_hint_of_the_invitation_templates_names_viindoo_discuss(self):
        for xmlid in (
            "calendar.calendar_template_meeting_invitation",
            "calendar.calendar_template_meeting_changedate",
            "calendar.calendar_template_meeting_reminder",
            "calendar.calendar_template_meeting_update",
        ):
            body = self.env.ref(xmlid).with_context(lang="en_US").body_html
            self.assertNotIn("Odoo Discuss", body, xmlid)
            self.assertIn("Join with Viindoo Discuss", body, xmlid)
