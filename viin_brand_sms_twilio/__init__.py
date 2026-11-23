from odoo.tools import config

from . import models
from . import tools


def _companies_through_odoo_after(setup_class_original):
    """Build a ``setUpClass`` that runs ``setup_class_original`` and then puts the companies on Odoo's gateway.

    Core suites on ``SMSCase`` and ``SMSCommon`` are written for a company that sends through Odoo:
    they read the ``sms.*`` settings of that gateway (such as the batch size) and mock that gateway.
    The write is made in the transaction of the test class and rolled back on teardown, so no
    committed data changes.

    :param setup_class_original: the ``setUpClass`` function to wrap
    :return: the wrapping ``classmethod``
    """
    def setUpClass(cls):
        setup_class_original(cls)
        # sudo: the provider is a company setting of administrators
        cls.env['res.company'].sudo().with_context(active_test=False).search([]).write({'sms_provider': 'iap'})
    setUpClass.realigned_for_odoo_gateway = True
    return classmethod(setUpClass)


def _realign_core_sms_company_provider():
    """Keep the companies of the core SMS suites on the gateway of Odoo.

    The company default of this module is Twilio, which core suites on ``SMSCase`` and
    ``SMSCommon`` do not expect: the batch size is read from the settings of Twilio and a send the
    suite makes under the mock of the gateway of Odoo goes to Twilio.
    """
    from odoo.addons.sms.tests.common import SMSCase, SMSCommon

    for suite_class in (SMSCase, SMSCommon):
        suite_class.setUpClass = _companies_through_odoo_after(suite_class.setUpClass.__func__)


def post_load():
    if config.get('test_enable', False):
        _realign_core_sms_company_provider()


def post_init_hook(env):
    """Move every company that sent SMS through Odoo to its own Twilio account."""
    env['res.company'].with_context(active_test=False).search([('sms_provider', '=', 'iap')]).write({
        'sms_provider': 'twilio',
    })
