from odoo import api, fields, models, tools
from odoo.tools.binary import BinaryBytes
from odoo.tools.misc import file_path

from ..controllers.webmanifest import VIINDOO_BRAND_COLOR, VIINDOO_THEME_COLOR


class Company(models.Model):
    _inherit = 'res.company'

    def _get_default_favicon(self):
        with tools.file_open(file_path('viin_brand/static/img/favicon.ico'), 'rb') as f:
            return BinaryBytes(f.read())

    favicon = fields.Binary(
        string="Company Favicon",
        help="This field holds the image used to display a favicon for a given company.",
        default=_get_default_favicon,
    )
    # The colours of the layout of the documents: core leaves them empty and derives them from the
    # logo, which for the placeholder logo is a mauve of the Odoo family. The primary colour is the
    # deep teal of the frame, the secondary the purple of the content.
    primary_color = fields.Char(default=VIINDOO_THEME_COLOR)
    secondary_color = fields.Char(default=VIINDOO_BRAND_COLOR)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('favicon'):
                vals['favicon'] = self._get_default_favicon()
        return super().create(vals_list)
