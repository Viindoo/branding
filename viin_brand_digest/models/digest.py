from odoo import models

from odoo.addons.digest.models.digest import ODOO_ICONS_CDN_URL

from .digest_tip import NO_ODOO_IMAGE_TIP_CONTEXT


class DigestDigest(models.Model):
    _inherit = 'digest.digest'

    def _compute_kpis(self, company, user):
        """Point the icon of each KPI to the image served by this database.

        Core builds the icon URL on the content network of Odoo S.A., where the Viindoo icons of
        the modules do not exist; the path alone is kept, and the rendering of the email turns it
        into a link on the URL of the database.
        """
        kpis = super()._compute_kpis(company, user)
        for kpi in kpis:
            kpi['kpi_icon'] = kpi['kpi_icon'].removeprefix(ODOO_ICONS_CDN_URL)
        return kpis

    def _compute_tips(self, company, user, tips_count=1, consumed=True):
        """Pick the tips as core does, among the tips that load no image from the servers of Odoo."""
        digest = self.with_context(**{NO_ODOO_IMAGE_TIP_CONTEXT: True})
        return super(DigestDigest, digest)._compute_tips(company, user, tips_count=tips_count, consumed=consumed)
