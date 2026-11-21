from . import models
from .models.ir_ui_menu import HIDDEN_MENU_XMLIDS


def uninstall_hook(env):
    env['ir.ui.menu']._restore_hidden_menus(HIDDEN_MENU_XMLIDS)
