from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import config


@tagged('post_install', '-at_install')
class TestIapInstallGuard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Module = cls.env['ir.module.module']
        cls.iap_module = Module.search([('name', '=', 'iap_crm')])
        cls.iap_module.state = 'uninstalled'
        cls.other_module = Module.search([('name', '=', 'mail')])
        cls.other_module.state = 'uninstalled'

    def _from_ui(self, init=None, update=None):
        request_patch = patch('odoo.addons.viin_brand.models.ir_module_module.request', new=object())
        config_patch = patch.dict(config.options.maps[0], {'init': init or {}, 'update': update or {}})
        self.enterContext(request_patch)
        self.enterContext(config_patch)

    def test_explicit_install_of_an_iap_module_from_the_ui_is_refused(self):
        self._from_ui()

        with self.assertRaises(UserError):
            self.iap_module.button_immediate_install()

    def test_install_or_update_option_lets_the_iap_module_through(self):
        for option in ('init', 'update'):
            with self.subTest(option=option):
                self._from_ui(**{option: {'iap_crm': True}})

                self.iap_module._check_iap_modules_are_not_requested()

    def test_a_script_without_http_request_is_not_refused(self):
        with patch.dict(config.options.maps[0], {'init': {}, 'update': {}}):
            self.iap_module._check_iap_modules_are_not_requested()

    def test_other_modules_are_not_refused(self):
        self._from_ui()

        self.other_module._check_iap_modules_are_not_requested()

    def test_iap_module_reached_as_a_dependency_is_not_refused(self):
        """Dependencies and auto-installed modules go through ``button_install``, not the UI entry."""
        self._from_ui()

        self.iap_module.button_install()

        self.assertEqual(self.iap_module.state, 'to install')
