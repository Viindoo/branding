import re

from odoo import api, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def load_demo_data(self):
        super().load_demo_data()
        self._neutralise_scenario_data()

    def _load_scenario(self):
        super()._load_scenario()
        self._neutralise_scenario_data()

    def _neutralise_scenario_data(self):
        """Describe the job position of the scenario data a user loads by choice without naming a product.

        The text is a sample job description of the customer's own company.
        """
        job = self.env.ref('hr.job_ceo', raise_if_not_found=False)
        if job:
            # the sample job belongs to the main company; core loads the scenario with sudo too
            job = job.sudo()
            if job.description:
                job.description = re.sub(r'\bOdoo\s+', '', job.description)
