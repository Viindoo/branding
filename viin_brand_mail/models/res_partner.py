from odoo import SUPERUSER_ID, api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _clear_installation_history_naming_odoo(self, xmlid):
        """Drop the history lines the installation itself wrote on a system partner and that name Odoo.

        The renaming of a system partner at installation is not a change a user made. A line written by a
        user stays, whatever it says.
        """
        partner = self.env.ref(xmlid, raise_if_not_found=False)
        if not partner:
            return
        self.env['mail.message'].search([
            ('model', '=', 'res.partner'),
            ('res_id', '=', partner.id),
            ('message_type', '=', 'tracking'),
            ('create_uid', '=', SUPERUSER_ID),
            ('body', 'ilike', 'odoo'),
        ]).unlink()
