from . import models


def _update_viindoo_theme(env):
    users = env['res.users'].with_context(active_test=False).search([])
    users.write({'apps_menu_theme': 'viindoo'})


def post_init_hook(env):
    _update_viindoo_theme(env)
