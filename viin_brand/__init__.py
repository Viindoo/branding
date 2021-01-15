from odoo import SUPERUSER_ID, api
from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['mail.template'].search([]).replace_brand()
    env['ir.ui.view'].search([]).replace_brand()