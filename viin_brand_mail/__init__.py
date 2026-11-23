from odoo import tools

from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR

from . import models
from . import wizard

if tools.config.get('test_enable', False):
    from odoo.addons.mail.tests.common import MailCase, MailCommon
    from odoo.addons.mail.tests.discuss.test_ui import TestUi as CoreDiscussTestUi

    from odoo.addons.viin_brand import get_viin_brand_module_icon


def _restore_core_bot_branding_fixture(owner):
    """Build a ``setUpClass`` for ``owner`` that restores the OdooBot name and email on ``base.partner_root``.

    The core suites that derive from ``MailCase`` (``MailCommon`` included) or from the Discuss
    ``TestUi`` hardcode the stock bot naming. The write happens in the transaction of the test
    class and is rolled back on teardown, so no committed data changes.

    The wrapper continues the chain of ``setUpClass`` of the class under test, never a function
    captured at patch time: a suite built on ``MailCase`` and ``HttpCase`` at once has
    ``HttpCase.setUpClass`` right after ``MailCase`` in its method resolution order, and a captured
    ``TransactionCase.setUpClass`` would skip it.

    :param type owner: the class whose ``setUpClass`` is wrapped
    :return: the wrapping ``classmethod``
    """
    own_setup = owner.__dict__.get('setUpClass')

    def setUpClass(cls):
        if own_setup is not None:
            own_setup.__func__(cls)
        else:
            super(owner, cls).setUpClass()
        partner_root = cls.env.ref('base.partner_root', raise_if_not_found=False)
        if partner_root:
            # sudo: restores a record of another module inside the test transaction
            partner_root.sudo().write({'name': 'OdooBot', 'email': 'odoobot@example.com'})
    return classmethod(setUpClass)


def _patch_mailcommon_module_icon_expectation():
    """Realign the core mail Store tests to the Viindoo module icon.

    Several core suites hardcode the stock icon of a module in the expected ``module_icon`` of
    their Store payloads, all built through ``MailCommon._filter_threads_fields``. The expected
    icon is resolved with the same function the Store uses, so the tests assert the Viindoo icon.
    """
    _filter_threads_fields_orig = MailCommon._filter_threads_fields

    def _filter_threads_fields(self, /, *threads_data):
        data_list = _filter_threads_fields_orig(self, *threads_data)
        for data in data_list:
            model = data.get('model')
            if 'module_icon' in data and model and model in self.env:
                data['module_icon'] = get_viin_brand_module_icon(self.env[model]._original_module)
        return data_list

    MailCommon._filter_threads_fields = _filter_threads_fields


def post_load():
    if not tools.config.get('test_enable', False):
        return
    _patch_mailcommon_module_icon_expectation()
    # ``MailCommon`` and the suites of ``mail`` that derive from ``MailCase`` alone share it.
    MailCase.setUpClass = _restore_core_bot_branding_fixture(MailCase)
    # TestUi derives from HttpCase, which ~30 unrelated suites share, so it is wrapped itself and
    # not its base class.
    CoreDiscussTestUi.setUpClass = _restore_core_bot_branding_fixture(CoreDiscussTestUi)


def post_init_hook(env):
    # Companies that still hold the stock outgoing-notification button colour of mail get the
    # Viindoo brand colour; a colour the customer chose is left untouched.
    # sudo: the hook runs at install with no user, over every company
    env['res.company'].sudo().search([('email_secondary_color', '=', '#875A7B')]).write({
        'email_secondary_color': VIINDOO_BRAND_COLOR,
    })
