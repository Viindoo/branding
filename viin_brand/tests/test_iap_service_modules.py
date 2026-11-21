from odoo.modules.module import Manifest
from odoo.tests.common import TransactionCase, tagged

from ..models.ir_module_module import IAP_SERVICE_MODULES


@tagged('post_install', '-at_install')
class TestIapServiceModules(TransactionCase):
    """The modules that sell Odoo IAP credits are not installed with a new database."""

    def test_service_modules_are_not_auto_installed(self):
        self.assertEqual(
            set(IAP_SERVICE_MODULES),
            {'crm_iap_enrich', 'crm_iap_mine', 'website_crm_iap_reveal', 'snailmail', 'snailmail_account'},
        )
        for name in IAP_SERVICE_MODULES:
            with self.subTest(module=name):
                manifest = Manifest.for_addon(name, display_warning=False)
                self.assertIsNotNone(manifest, "%s is not on the addons path" % name)
                self.assertIs(manifest['auto_install'], False)

    def test_other_modules_keep_their_auto_install(self):
        manifest = Manifest.for_addon('iap_mail', display_warning=False)
        self.assertTrue(manifest['auto_install'])
