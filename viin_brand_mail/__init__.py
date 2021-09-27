from odoo import SUPERUSER_ID, api
from . import models


def _get_debranding_words_map():
    return [
        ('Odoo', 'Viindoo'),
        ('odoo.com', 'viindoo.com'),
        ('openerp.com', 'viindoo.com')
    ]


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['mail.template'].with_context(active_test=False).search([])._viindoo_debrand()
    env['ir.ui.view'].with_context(active_test=False).search([])._viindoo_debrand()
