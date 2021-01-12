from odoo import api, SUPERUSER_ID

from odoo.addons.viin_brand import _update_viin_brand_module_icon, _update_viin_brand_web_icon


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_viin_brand_module_icon(env)
    _update_viin_brand_web_icon(env)

