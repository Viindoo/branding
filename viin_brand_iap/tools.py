from urllib.parse import urlsplit

from odoo.exceptions import AccessError, UserError
from odoo.tools.translate import LazyTranslate

from odoo.addons.iap.tools.iap_tools import IAPServerError

_lt = LazyTranslate(__name__)

# The endpoints of the services that Odoo S.A. bills in IAP credits. The free background services
# (website configurator, text generation, text translation) are served by other hosts and are not
# listed.
PAID_IAP_HOSTS = frozenset({
    'iap.odoo.com',
    'iap-services.odoo.com',
    'partner-autocomplete.odoo.com',
    'sms.api.odoo.com',
    'iap-snailmail.odoo.com',
})


def is_paid_service(url):
    """Tell whether ``url`` points to a credit-based service of Odoo S.A."""
    return urlsplit(url).hostname in PAID_IAP_HOSTS


def refuse_paid_service():
    """Refuse an action that opens a credit-based service of Odoo S.A.

    :raises AccessError: always, with a message that names Viindoo
    """
    raise AccessError(_lt("This service is not available on Viindoo."))


def refuse_paid_service_request(raise_user_error=False):
    """Refuse a JSON-RPC request to a credit-based service of Odoo S.A.

    The refusal is the failure that ``iap_jsonrpc`` itself reports, so a caller handles it as it
    handles an unreachable service.

    :param bool raise_user_error: whether the caller asked ``iap_jsonrpc`` for a ``UserError``
    :raises UserError: when ``raise_user_error`` is set
    :raises IAPServerError: otherwise (a ``requests.RequestException``)
    """
    message = _lt("This service is not available on Viindoo.")
    if raise_user_error:
        raise UserError(message)
    raise IAPServerError(message)
