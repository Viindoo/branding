from odoo import api, fields, models

from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR

# The colour that Events gives a ticket when it has none of its own, written as a literal in its field.
ODOO_TICKET_COLOUR = '#875A7B'


class EventEventTicket(models.Model):
    _inherit = 'event.event.ticket'

    color = fields.Char(default=lambda self: VIINDOO_BRAND_COLOR)

    @api.model
    def _recolour_demo_tickets(self):
        """Give the demo tickets that the module Events ships the colour a new ticket gets.

        The demo of Events is loaded before the default of this module exists, so its tickets carry
        the colour of Events. The demo data of this module calls this method when the module is
        installed, and never when it is updated. A ticket is changed only when the module Events
        created it from its own data files and it still has the colour of Events: a ticket that a
        user created or imported, or whose colour a user changed, is left as it is.
        """
        shipped = self.env['ir.model.data'].search([('module', '=', 'event'), ('model', '=', self._name)])
        tickets = self.browse(shipped.mapped('res_id')).exists()
        with_the_colour_of_events = tickets.filtered(lambda ticket: ticket.color == ODOO_TICKET_COLOUR)
        with_the_colour_of_events.color = self.default_get(['color'])['color']
