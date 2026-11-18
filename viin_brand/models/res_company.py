import base64

from odoo import api, fields, models, tools
from odoo.tools.misc import file_path


class Company(models.Model):
    _inherit = 'res.company'

    def _get_default_favicon(self):
        with tools.file_open(file_path('viin_brand/static/img/favicon.ico'), 'rb') as f:
            return base64.b64encode(f.read())

    favicon = fields.Binary(
        string="Company Favicon",
        help="This field holds the image used to display a favicon for a given company.",
        default=_get_default_favicon,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('favicon'):
                vals['favicon'] = self._get_default_favicon()
        return super().create(vals_list)
