from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import config


@tagged('post_install', '-at_install')
class TestIapInstallGuard(TransactionCase):

    @classmethod
    def _module(cls, name):
        """The module record of ``name``, a stub when no addons path carries it."""
        Module = cls.env['ir.module.module']
        module = Module.search([('name', '=', name)]) or Module.create({'name': name})
        module.state = 'uninstalled'
        return module

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.iap_module = cls._module('iap_crm')
        cls.other_module = cls._module('other_module_stub')

    def _from_ui(self, init=None, update=None):
        request_patch = patch('odoo.addons.viin_brand.models.ir_module_module.request', new=object())
        config_patch = patch.dict(config.options.maps[0], {'init': init or {}, 'update': update or {}})
        self.enterContext(request_patch)
        self.enterContext(config_patch)

    def test_explicit_install_of_an_iap_module_from_the_ui_is_refused(self):
        self._from_ui()

        with self.assertRaises(UserError):
            self.iap_module.button_immediate_install()

    def test_every_service_module_is_refused_from_the_ui(self):
        self._from_ui()
        for name in ('crm_iap_enrich', 'crm_iap_mine', 'website_crm_iap_reveal', 'snailmail', 'snailmail_account'):
            with self.subTest(module=name):
                module = self._module(name)

                with self.assertRaises(UserError):
                    module.button_immediate_install()

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
