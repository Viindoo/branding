from odoo.modules.module import Manifest
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRetiredShell(TransactionCase):

    def test_the_retired_base_setup_shell_is_free(self):
        manifest = Manifest.for_addon('viin_brand_base_setup', display_warning=False)
        self.assertEqual(manifest['price'], 0.0)
