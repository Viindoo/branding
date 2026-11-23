from odoo import models
from odoo.exceptions import UserError

from odoo.addons.viin_brand.tools import debrand_exception


class HrLeaveGenerateMultiWizard(models.TransientModel):
    _inherit = 'hr.leave.generate.multi.wizard'

    def action_generate_time_off(self):
        """Raise the errors of the batch generation with the Viindoo name."""
        try:
            return super().action_generate_time_off()
        except UserError as error:
            raise debrand_exception(error) from None
