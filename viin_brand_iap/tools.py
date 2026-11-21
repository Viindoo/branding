from urllib.parse import urlsplit

from odoo.exceptions import AccessError
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)

# The endpoints of the services that Odoo S.A. bills in IAP credits. The free background services
# (website configurator, text generation) are served by other hosts and are not listed.
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
    """Refuse a request to a credit-based service of Odoo S.A.

    :raises AccessError: always, with a message that names Viindoo
    """
    raise AccessError(_lt("This service is not available on Viindoo."))
