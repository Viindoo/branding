# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from datetime import timedelta

from odoo import Command, fields
from odoo.tests import Form, TransactionCase, tagged

from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR

CORE_TICKET_COLOUR = "#875A7B"
USER_COLOUR = "#123456"


@tagged("post_install", "-at_install")
class TestTicketColour(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now = fields.Datetime.now()
        cls.event = cls.env["event.event"].create({
            "name": "Colour event",
            "date_begin": now + timedelta(days=1),
            "date_end": now + timedelta(days=2),
            "event_ticket_ids": [Command.create({"name": "Standard"})],
        })
        cls.ticket = cls.event.event_ticket_ids

    def _badge_html(self, badge_format):
        self.event.badge_format = badge_format
        html, _report_type = self.env["ir.actions.report"]._render_qweb_html(
            "event.action_report_event_event_badge", self.event.ids,
        )
        return html.decode().lower()

    def test_a_new_ticket_line_of_an_event_takes_the_viindoo_purple(self):
        """A ticket line added on the form of an event gets the Viindoo content purple, and a colour
        the user picks on the line is kept.

        WOULD FAIL IF REVERTED: without the default of this module the line takes the Odoo purple
        of core."""
        with Form(self.env["event.event"]) as event_form:
            event_form.name = "Ticket colour event"
            with event_form.event_ticket_ids.new() as line:
                line.name = "Default colour"
                self.assertEqual(line.color.upper(), VIINDOO_BRAND_COLOR.upper())
            with event_form.event_ticket_ids.new() as line:
                line.name = "Chosen colour"
                line.color = USER_COLOUR
        tickets = event_form.record.event_ticket_ids
        self.assertEqual(
            tickets.filtered(lambda ticket: ticket.name == "Default colour").color.upper(),
            VIINDOO_BRAND_COLOR.upper(),
        )
        self.assertEqual(tickets.filtered(lambda ticket: ticket.name == "Chosen colour").color, USER_COLOUR)

    def test_the_printed_badge_paints_the_ticket_band_with_the_viindoo_purple(self):
        """On each badge format the band of the ticket name has the colour of the ticket, and a
        ticket with no colour takes the colour a new ticket gets, never the Odoo purple of core.

        WOULD FAIL IF REVERTED: without the templates of this module the band of a ticket with no
        colour is the Odoo purple, on the foldable badge and on the card of the other formats."""
        for badge_format in ("A4_french_fold", "four_per_sheet", "A6"):
            with self.subTest(badge_format=badge_format, ticket="no colour"):
                self.ticket.color = False
                html = self._badge_html(badge_format)
                self.assertIn("background-color: %s" % VIINDOO_BRAND_COLOR.lower(), html)
                self.assertNotIn(CORE_TICKET_COLOUR.lower(), html)
            with self.subTest(badge_format=badge_format, ticket="own colour"):
                self.ticket.color = USER_COLOUR
                html = self._badge_html(badge_format)
                self.assertIn("background-color: %s" % USER_COLOUR, html)
                self.assertNotIn(VIINDOO_BRAND_COLOR.lower(), html)
