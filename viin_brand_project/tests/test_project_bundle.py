from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestProjectBundle(TransactionCase):
    """The project sharing page loads its own asset bundle, which holds none of the backend patches."""

    def test_project_sharing_dialogs_and_errors_name_viindoo(self):
        bundle = self.env['ir.qweb']._get_asset_bundle('project.webclient', css=False, js=True, debug_assets=True)
        js = (bundle.js().raw or b'').decode('utf-8', 'replace')
        self.assertIn('Viindoo Error', js)
