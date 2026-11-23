from odoo import api, fields, models
from odoo.fields import Domain

# The images of many tips of Odoo are screenshots of the Odoo interface loaded from this host.
ODOO_IMAGE_HOST = 'odoocdn.com'
NO_ODOO_IMAGE_TIP_CONTEXT = 'viin_brand_digest_no_odoo_image_tip'


class DigestTip(models.Model):
    _inherit = 'digest.tip'

    active = fields.Boolean(string="Active", default=True)

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        """Leave out the tips that load an image from the servers of Odoo when a digest picks its tips."""
        if self.env.context.get(NO_ODOO_IMAGE_TIP_CONTEXT):
            domain = Domain(domain) & Domain('tip_description', 'not ilike', ODOO_IMAGE_HOST)
        return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)
