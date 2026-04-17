from odoo import SUPERUSER_ID, api

from odoo.addons.viin_brand_auth_signup import _force_branding_translations


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    _force_branding_translations(env)
