from odoo import api, models


class AuthPasskeyKey(models.Model):
    _inherit = 'auth.passkey.key'

    @api.model
    def _start_registration(self):
        """Present the site as Viindoo in the passkey enrolment prompt of the browser and device."""
        registration_options = super()._start_registration()
        registration_options['rp']['name'] = 'Viindoo'
        return registration_options
