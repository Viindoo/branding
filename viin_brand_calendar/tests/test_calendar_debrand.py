# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged

INVITATION_TEMPLATES = (
    "calendar.calendar_template_meeting_invitation",
    "calendar.calendar_template_meeting_changedate",
    "calendar.calendar_template_meeting_reminder",
)


@tagged("post_install", "-at_install")
class TestCalendarDebrand(TransactionCase):

    def _event(self, alarms=None):
        return self.env["calendar.event"].with_context(no_mail_to_attendees=True).create({
            "name": "Kick-off",
            "start": "2026-03-02 09:00:00",
            "stop": "2026-03-02 10:00:00",
            "partner_ids": [(4, self.env.ref("base.partner_admin").id)],
            "alarm_ids": [(6, 0, alarms.ids)] if alarms else [],
        })

    def test_invitation_alarm_without_a_name_is_described_as_viindoo(self):
        alarm = self.env["calendar.alarm"].create(
            {"name": "", "alarm_type": "notification", "duration": 10, "interval": "minutes"},
        )
        event = self._event(alarm)

        ics = event._get_ics_file()[event.id].decode()

        self.assertIn("DESCRIPTION:Viindoo\r\n", ics)
        self.assertNotIn("DESCRIPTION:Odoo", ics)

    def test_invitation_alarm_keeps_the_name_it_has(self):
        alarm = self.env["calendar.alarm"].create(
            {"name": "Ten minutes before", "alarm_type": "notification", "duration": 10, "interval": "minutes"},
        )
        event = self._event(alarm)

        ics = event._get_ics_file()[event.id].decode()

        self.assertIn("DESCRIPTION:Ten minutes before", ics)

    def _discuss_event(self):
        event = self._event()
        event.write({
            "videocall_source": "discuss",
            "videocall_location": event.get_base_url() + "/calendar/join_videocall/kickoff",
        })
        return event

    def test_the_videocall_of_an_attendee_mail_is_named_after_viindoo_in_every_language(self):
        event = self._discuss_event()
        attendee = event.attendee_ids[:1]
        self.env["res.lang"]._activate_lang("vi_VN")
        for xmlid in INVITATION_TEMPLATES:
            template = self.env.ref(xmlid)
            for lang in ("en_US", "vi_VN"):
                body = template._render_field("body_html", attendee.ids, set_lang=lang)[attendee.id]
                with self.subTest(template=xmlid, lang=lang):
                    self.assertIn("Viindoo Discuss", body)
                    self.assertNotIn("Odoo Discuss", body)

    def test_the_videocall_of_the_update_mail_is_named_after_viindoo(self):
        event = self._discuss_event()
        body = self.env.ref("calendar.calendar_template_meeting_update")._render_field(
            "body_html", event.ids,
        )[event.id]

        self.assertIn("Viindoo Discuss", body)
        self.assertNotIn("Odoo Discuss", body)
