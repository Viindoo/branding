import functools
import inspect

from . import models
from .models.ir_ui_menu import HIDDEN_MENU_XMLIDS
from .tools import is_paid_service, refuse_paid_service_request

guarded_iap_jsonrpc = None


def _refuse_paid_services(iap_jsonrpc):
    """Wrap ``iap_jsonrpc`` so that a call to a credit-based service of Odoo S.A. never leaves the server.

    :param iap_jsonrpc: the function to wrap
    :return: the wrapped function; a call to any other host is passed to ``iap_jsonrpc`` unchanged
    :raises requests.RequestException: from the wrapped function, when the host of ``url`` is a
        paid service; a ``UserError`` when the caller asked for one with ``raise_user_error``
    """
    signature = inspect.signature(iap_jsonrpc)

    @functools.wraps(iap_jsonrpc)
    def refusing_iap_jsonrpc(url, *args, **kwargs):
        if is_paid_service(url):
            arguments = signature.bind(url, *args, **kwargs).arguments
            refuse_paid_service_request(arguments.get('raise_user_error', False))
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
