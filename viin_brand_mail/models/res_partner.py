from odoo import api, models, tools


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _viin_brand_restore_bot_test_identity(self):
        """Put `base.partner_root` back to core's OdooBot identity while tests are running.

        Core ships a large number of tests that hardcode the vanilla identity
        (`odoobot@example.com` / `OdooBot`) - `google_calendar`'s Odoo-to-Google payload
        comparisons are the widest set, since the superuser is the implicit event organiser there.
        Rebranding it breaks every one of them, so the branding is undone for the duration of a
        test run.

        Why this is called from `data/res_partner_data.xml` and not only from `post_init_hook`:
        that data file is not `noupdate`, so the rebranding is re-applied on EVERY module update,
        whereas `odoo/modules/loading.py:244` calls `post_init_hook` only when the module's state
        is `to install` (`:178`). The two were therefore asymmetric - branding on every load, the
        restore on the first one only - and any `-u` left the partner branded, turning 17 core
        tests red for reasons that had nothing to do with the code under test. Driving both from
        the same data file keeps them on one trigger.
        """
        if not tools.config.get('test_enable', False):
            return
        partner_root = self.env.ref('base.partner_root', raise_if_not_found=False)
        if partner_root:
            partner_root.write({'name': 'OdooBot', 'email': 'odoobot@example.com'})
