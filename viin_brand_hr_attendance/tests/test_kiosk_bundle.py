from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestKioskBundle(TransactionCase):
    """The public kiosk loads its own asset bundle, which holds none of the backend patches."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        bundle = cls.env['ir.qweb']._get_asset_bundle(
            'hr_attendance.assets_public_attendance', css=False, js=True, debug_assets=True,
        )
        cls.js = (bundle.js().raw or b'').decode('utf-8', 'replace')

    def test_the_kiosk_footer_is_powered_by_viindoo(self):
        self.assertIn('Viindoo Logo', self.js)

    def test_the_kiosk_dialogs_and_errors_name_viindoo(self):
        self.assertIn('Viindoo Error', self.js)

    def test_the_kiosk_documentation_link_opens_the_viindoo_page(self):
        self.assertIn('set-up-the-attendance-kiosk', self.js)
