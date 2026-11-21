import functools

from . import models
from .models.ir_ui_menu import HIDDEN_MENU_XMLIDS
from .tools import is_paid_service, refuse_paid_service

guarded_iap_jsonrpc = None


def _refuse_paid_services(iap_jsonrpc):
    """Wrap ``iap_jsonrpc`` so that a call to a credit-based service of Odoo S.A. never leaves the server.

    :param iap_jsonrpc: the function to wrap
    :return: the wrapped function; a call to any other host is passed to ``iap_jsonrpc`` unchanged
    :raises AccessError: from the wrapped function, when the host of ``url`` is a paid service
    """
    @functools.wraps(iap_jsonrpc)
    def refusing_iap_jsonrpc(url, *args, **kwargs):
        if is_paid_service(url):
            refuse_paid_service()
        return iap_jsonrpc(url, *args, **kwargs)

    return refusing_iap_jsonrpc


def post_load():
    """Guard the process-wide IAP entry points: every caller reaches the service through them."""
    import odoo.addons.iap as iap
    from odoo.addons.iap.tools import iap_tools

    global guarded_iap_jsonrpc
    if iap_tools.iap_jsonrpc is guarded_iap_jsonrpc:
        return
    guarded_iap_jsonrpc = _refuse_paid_services(iap_tools.iap_jsonrpc)
    iap_tools.iap_jsonrpc = guarded_iap_jsonrpc
    iap.jsonrpc = guarded_iap_jsonrpc


def uninstall_hook(env):
    env['ir.ui.menu']._restore_hidden_menus(HIDDEN_MENU_XMLIDS)
