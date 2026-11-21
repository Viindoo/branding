from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBackendBundle(TransactionCase):

    def test_the_attendances_empty_state_shows_the_viindoo_kiosk_picture(self):
        bundle = self.env['ir.qweb']._get_asset_bundle('web.assets_backend', css=False, js=True, debug_assets=True)
        js = (bundle.js().raw or b'').decode('utf-8', 'replace')
        self.assertIn('/viin_brand_hr_attendance/static/img/mock-tablet.png', js)
