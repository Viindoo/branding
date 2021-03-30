from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['mail.template'].with_context(active_test=False).search([])._viindoo_debrand()
    env['ir.ui.view'].with_context(active_test=False).search([])._viindoo_debrand()

