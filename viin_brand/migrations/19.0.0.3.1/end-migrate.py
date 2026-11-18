import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Remove viin_brand_web and viin_brand_base_setup unless an installed module needs them."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    shells = env['ir.module.module'].search([
        ('name', 'in', ['viin_brand_web', 'viin_brand_base_setup']),
        ('state', 'in', ['installed', 'to upgrade']),
    ])
    for shell in shells:
        dependents = shell.downstream_dependencies()
        if dependents:
            _logger.warning(
                "%s is kept because of the installed modules that depend on it: %s",
                shell.name, ", ".join(dependents.mapped('name')))
        else:
            shell.button_uninstall()
